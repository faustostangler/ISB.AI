import logging
import time
from unittest.mock import patch

import pytest
from prometheus_client import REGISTRY

from isb.shared_kernel.adapters.lock.in_mem import InMemLockAdapter


def test_in_mem_lock_success() -> None:
    """Scenario 1: Entering lock context manager acquires it, and exiting releases it."""
    lock_port = InMemLockAdapter()
    key = "lock:test-success"

    # Initially, lock should be free
    with lock_port.lock(key, lease_duration=5.0) as acquired:
        assert acquired is True
        # Attempting to acquire again in the same/another thread should fail
        assert lock_port.acquire(key, lease_duration=5.0, token="other-token") is False

    # After exit, lock must be free
    assert lock_port.acquire(key, lease_duration=5.0, token="new-token") is True
    lock_port.release(key, "new-token")


def test_in_mem_lock_exception() -> None:
    """Scenario 2: An unhandled exception occurs inside the block, but the lock is still released."""
    lock_port = InMemLockAdapter()
    key = "lock:test-exception"

    def trigger_error() -> None:
        with lock_port.lock(key, lease_duration=5.0) as acquired:
            assert acquired is True
            raise RuntimeError("Some error")

    with pytest.raises(RuntimeError, match="Some error"):
        trigger_error()

    # Lock must be released
    assert lock_port.acquire(key, lease_duration=5.0, token="new-token") is True
    lock_port.release(key, "new-token")


def test_in_mem_lock_empty_key() -> None:
    """Boundary Condition: Empty key must raise ValueError."""
    lock_port = InMemLockAdapter()

    with pytest.raises(ValueError, match="Lock key cannot be empty or None"):
        with lock_port.lock("", lease_duration=5.0):
            pass

    with pytest.raises(ValueError, match="Lock key cannot be empty or None"):
        with lock_port.lock("   ", lease_duration=5.0):
            pass


def test_in_mem_lock_blocking_timeout() -> None:
    """Scenario: Blocking acquisition should wait and eventually timeout if the lock is held."""
    lock_port = InMemLockAdapter()
    key = "lock:test-blocking"

    # Acquire once
    assert lock_port.acquire(key, lease_duration=10.0, token="token-1") is True

    # Try to acquire with blocking=True and a short timeout
    start_time = time.monotonic()
    acquired = lock_port.acquire(key, lease_duration=5.0, token="token-2", blocking=True, timeout=0.05)
    duration = time.monotonic() - start_time

    assert acquired is False
    assert duration >= 0.05
    assert duration < 0.2


def test_in_mem_lock_exact_expiry() -> None:
    """Boundary Condition: Verify lock is treated as expired if now >= expire_at exactly."""
    lock_port = InMemLockAdapter()
    key = "lock:test-exact-expiry"

    now = time.monotonic()
    lock_port._locks[key] = ("token-1", now)

    # Force time.monotonic() to return exactly `now` during acquire
    with patch("time.monotonic", return_value=now):
        assert lock_port.acquire(key, lease_duration=5.0, token="token-2") is True


def test_lock_telemetry(caplog: pytest.LogCaptureFixture) -> None:
    """Observability: Verify Prometheus metrics and warning logs for lock collisions."""
    lock_port = InMemLockAdapter()
    key = "lock:test:collision"

    with caplog.at_level(logging.WARNING):
        # 1. Acquire the lock once
        with lock_port.lock(key, lease_duration=10.0) as acquired1:
            assert acquired1 is True

            # Record Prometheus collisions count before
            collisions_before = REGISTRY.get_sample_value(
                "isb_lock_collisions_total",
                {"lock_key_prefix": "lock:test"}
            ) or 0.0

            # 2. Try to acquire the same lock (should fail and trigger warning/metric)
            with lock_port.lock(key, lease_duration=5.0) as acquired2:
                assert acquired2 is False

            # Verify metric incremented
            collisions_after = REGISTRY.get_sample_value(
                "isb_lock_collisions_total",
                {"lock_key_prefix": "lock:test"}
            ) or 0.0
            assert collisions_after == collisions_before + 1.0

        # Verify warning log was emitted
        assert any("Lock collision" in record.message for record in caplog.records)


def test_lock_telemetry_no_colon() -> None:
    """Observability: Verify lock key with no colon sets prefix to key itself."""
    lock_port = InMemLockAdapter()
    key = "nocolon"

    with lock_port.lock(key, lease_duration=10.0) as acquired1:
        assert acquired1 is True
        collisions_before = REGISTRY.get_sample_value(
            "isb_lock_collisions_total",
            {"lock_key_prefix": "nocolon"}
        ) or 0.0

        with lock_port.lock(key, lease_duration=5.0) as acquired2:
            assert acquired2 is False

        collisions_after = REGISTRY.get_sample_value(
            "isb_lock_collisions_total",
            {"lock_key_prefix": "nocolon"}
        ) or 0.0
        assert collisions_after == collisions_before + 1.0


def test_lock_telemetry_one_colon() -> None:
    """Observability: Verify lock key with exactly one colon extracts prefix correctly."""
    lock_port = InMemLockAdapter()
    key = "lock:collision"

    with lock_port.lock(key, lease_duration=10.0) as acquired1:
        assert acquired1 is True
        collisions_before = REGISTRY.get_sample_value(
            "isb_lock_collisions_total",
            {"lock_key_prefix": "lock"}
        ) or 0.0

        with lock_port.lock(key, lease_duration=5.0) as acquired2:
            assert acquired2 is False

        collisions_after = REGISTRY.get_sample_value(
            "isb_lock_collisions_total",
            {"lock_key_prefix": "lock"}
        ) or 0.0
        assert collisions_after == collisions_before + 1.0
