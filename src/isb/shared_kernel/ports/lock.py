import contextlib
import logging
import uuid
from abc import ABC, abstractmethod
from collections.abc import Generator

from prometheus_client import Counter, Histogram

logger = logging.getLogger("isb.lock")

# Prometheus metrics for distributed locking (Observability & Telemetry Assertions)
LOCK_ACQUIRE_DURATION = Histogram(
    "isb_lock_acquire_duration_seconds",
    "Time spent attempting to acquire lock",
)

LOCK_COLLISIONS_COUNTER = Counter(
    "isb_lock_collisions_total",
    "Total number of lock collision events",
    ["lock_key_prefix"],
)


def _extract_lock_prefix(key: str) -> str:
    """Helper to extract the base prefix from a lock key string.

    E.g., "lock:scrape:url:123" -> "lock:scrape:url"
    If no colon is present, returns the key itself.
    """
    parts = key.split(":")
    if len(parts) > 1:
        return ":".join(parts[:-1])
    return key


class LockPort(ABC):
    """Abstract Port representing a distributed lock."""

    @abstractmethod
    def acquire(
        self,
        key: str,
        lease_duration: float,
        token: str,
        blocking: bool = False,
        timeout: float = 0.0,
    ) -> bool:
        """Acquires a lock for the given key and lease duration.

        Args:
            key: The unique string identifying the resource to lock.
            lease_duration: Time in seconds before the lock is automatically released (TTL).
            token: Unique signature value used to identify this specific acquisition instance.
            blocking: Whether to block until the lock is acquired if already held.
            timeout: Maximum time in seconds to block before giving up.

        Returns:
            bool: True if lock acquired successfully, False otherwise.
        """
        pass

    @abstractmethod
    def release(self, key: str, token: str) -> None:
        """Releases the lock for the given key.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        pass

    @contextlib.contextmanager
    def lock(
        self,
        key: str,
        lease_duration: float,
        blocking: bool = False,
        timeout: float = 0.0,
    ) -> Generator[bool]:
        """Context manager to coordinate safe lock acquisition and release.

        Args:
            key: The unique string identifying the resource to lock.
            lease_duration: Time in seconds before the lock is automatically released (TTL).
            blocking: Whether to block until the lock is acquired if already held.
            timeout: Maximum time in seconds to block before giving up.

        Yields:
            bool: True if the lock was acquired, False otherwise.
        """
        if not key or not key.strip():
            raise ValueError("Lock key cannot be empty or None")

        token = uuid.uuid4().hex
        acquired = False
        try:
            with LOCK_ACQUIRE_DURATION.time():
                acquired = self.acquire(
                    key=key,
                    lease_duration=lease_duration,
                    token=token,
                    blocking=blocking,
                    timeout=timeout,
                )

            if acquired:
                logger.debug("Lock acquired successfully. Key=%s, Token=%s", key, token)
            else:
                prefix = _extract_lock_prefix(key)
                LOCK_COLLISIONS_COUNTER.labels(lock_key_prefix=prefix).inc()
                logger.warning(
                    "Lock collision: Attempt to acquire already held lock. Key=%s", key
                )

            yield acquired
        finally:
            if acquired:
                self.release(key=key, token=token)
                logger.debug("Lock released successfully. Key=%s, Token=%s", key, token)
