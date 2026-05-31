import time
from unittest.mock import MagicMock, patch

import pytest
import redis

from isb.config import settings
from isb.shared_kernel.adapters.lock.redis import RedisLockAdapter

# Check if a live Redis instance is available
try:
    client = redis.Redis.from_url(settings.REDIS_URL)
    client.ping()
    redis_available = True
except Exception:
    redis_available = False

skip_if_no_redis = pytest.mark.skipif(
    not redis_available,
    reason="Redis server is not running on local port 6379"
)


# --- Unit Tests with Mocks (Hermetic & Mutation Testing coverage) ---

def test_redis_lock_adapter_default_init() -> None:
    """Verifies that RedisLockAdapter initializes a Redis client using settings.REDIS_URL by default."""
    with patch("redis.Redis.from_url") as mock_from_url:
        adapter = RedisLockAdapter()
        assert adapter._redis == mock_from_url.return_value
        mock_from_url.assert_called_once_with(settings.REDIS_URL, decode_responses=True)


def test_redis_lock_acquire_mock() -> None:
    """Verifies that RedisLockAdapter calls SET with correct lock parameters on the mock Redis client."""
    mock_redis = MagicMock(spec=redis.Redis)
    adapter = RedisLockAdapter(redis_client=mock_redis)

    # Mock SET returning True (acquired)
    mock_redis.set.return_value = True

    acquired = adapter.acquire(key="lock:test", lease_duration=5.0, token="my-token")
    assert acquired is True
    mock_redis.set.assert_called_once_with("lock:test", "my-token", nx=True, px=5000)


def test_redis_lock_acquire_fail_mock() -> None:
    """Verifies that RedisLockAdapter returns False when non-blocking acquire fails."""
    mock_redis = MagicMock(spec=redis.Redis)
    adapter = RedisLockAdapter(redis_client=mock_redis)

    # SET returns None (not acquired)
    mock_redis.set.return_value = None

    acquired = adapter.acquire(key="lock:test", lease_duration=5.0, token="my-token", blocking=False)
    assert acquired is False


def test_redis_lock_acquire_blocking_timeout_mock() -> None:
    """Verifies that RedisLockAdapter blocks and times out correctly when lock is already held."""
    mock_redis = MagicMock(spec=redis.Redis)
    adapter = RedisLockAdapter(redis_client=mock_redis)

    # SET returns None (not acquired)
    mock_redis.set.return_value = None

    start_time = time.monotonic()
    acquired = adapter.acquire(key="lock:test", lease_duration=5.0, token="my-token", blocking=True, timeout=0.05)
    duration = time.monotonic() - start_time

    assert acquired is False
    assert duration >= 0.05
    assert duration < 0.2
    # Verify set was called multiple times because of the polling loop
    assert mock_redis.set.call_count > 1


def test_redis_lock_release_mock() -> None:
    """Verifies that RedisLockAdapter executes the correct atomic Lua script on release."""
    mock_redis = MagicMock(spec=redis.Redis)
    adapter = RedisLockAdapter(redis_client=mock_redis)

    adapter.release(key="lock:test", token="my-token")

    # Assert eval is called with matching release Lua script
    mock_redis.eval.assert_called_once()
    args, _ = mock_redis.eval.call_args
    script = args[0]
    assert "redis.call(\"get\", KEYS[1]) == ARGV[1]" in script
    assert "redis.call(\"del\", KEYS[1])" in script
    assert args[1] == 1  # numkeys
    assert args[2] == "lock:test"  # KEYS[1]
    assert args[3] == "my-token"  # ARGV[1]


# --- Live Integration Tests ---

@skip_if_no_redis
@pytest.mark.integration
def test_redis_lock_integration_flow() -> None:
    """Scenario 3: Verify end-to-end locking and mismatched token protection on live Redis."""
    redis_client = redis.Redis.from_url(settings.REDIS_URL)
    adapter1 = RedisLockAdapter(redis_client=redis_client)
    adapter2 = RedisLockAdapter(redis_client=redis_client)
    key = "lock:integration:test"

    # Ensure key is clean
    redis_client.delete(key)

    # 1. Adapter 1 acquires the lock
    with adapter1.lock(key, lease_duration=2.0) as acquired1:
        assert acquired1 is True

        # 2. Adapter 2 attempts to acquire the same lock (should fail)
        with adapter2.lock(key, lease_duration=2.0) as acquired2:
            assert acquired2 is False

        # 3. Simulate Client A attempting to release with a mismatched token
        # Our context manager uses a generated UUID, let's verify that releasing with a fake token is a no-op
        # and doesn't delete the key
        adapter1.release(key, "fake-token")
        assert redis_client.exists(key) == 1

    # 4. After exit, the context manager should release the lock (using correct token)
    assert redis_client.exists(key) == 0


@skip_if_no_redis
@pytest.mark.integration
def test_redis_lock_lease_expiration() -> None:
    """Verifies that the lock is automatically released after lease expiration."""
    redis_client = redis.Redis.from_url(settings.REDIS_URL)
    adapter = RedisLockAdapter(redis_client=redis_client)
    key = "lock:integration:expiration"

    # Ensure key is clean
    redis_client.delete(key)

    # Acquire with very short TTL
    assert adapter.acquire(key, lease_duration=0.5, token="expire-token") is True
    assert redis_client.exists(key) == 1

    # Wait for TTL to expire
    time.sleep(0.6)

    # Now it should be expired and another client can acquire it
    assert redis_client.exists(key) == 0
