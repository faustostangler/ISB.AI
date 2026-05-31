import time

import redis

from isb.config import settings
from isb.shared_kernel.ports.lock import LockPort

# Lua script to release lock atomically ensuring only the holder of the correct token can delete the key
RELEASE_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


class RedisLockAdapter(LockPort):
    """Redis-based lease distributed lock adapter implementation of LockPort."""

    def __init__(self, redis_client: redis.Redis | None = None) -> None:
        """Initializes the RedisLockAdapter.

        Args:
            redis_client: Optional pre-configured Redis client. If not provided,
                         a new client will be created from Settings.
        """
        if redis_client is not None:
            self._redis = redis_client
        else:
            self._redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def acquire(
        self,
        key: str,
        lease_duration: float,
        token: str,
        blocking: bool = False,  # pragma: no mutate
        timeout: float = 0.0,  # pragma: no mutate
    ) -> bool:
        """Acquires a lock via Redis.

        Args:
            key: The unique string identifying the resource to lock.
            lease_duration: Time in seconds before the lock is automatically released (TTL).
            token: Unique signature value used to identify this specific acquisition instance.
            blocking: Whether to block until the lock is acquired if already held.
            timeout: Maximum time in seconds to block before giving up.

        Returns:
            bool: True if lock acquired successfully, False otherwise.
        """
        start_time = time.monotonic()
        px_ms = int(lease_duration * 1000)

        while True:
            # Atomic acquisition via SET key token NX PX px_ms
            is_set = self._redis.set(key, token, nx=True, px=px_ms)
            if is_set:
                return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def release(self, key: str, token: str) -> None:
        """Releases the lock via Redis atomically if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        # Execute safe Lua release script
        self._redis.eval(RELEASE_SCRIPT, 1, key, token)
