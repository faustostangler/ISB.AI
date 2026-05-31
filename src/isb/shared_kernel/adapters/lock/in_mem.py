import threading
import time

from isb.shared_kernel.ports.lock import LockPort


class InMemLockAdapter(LockPort):
    """In-memory thread-safe adapter implementation of the LockPort."""

    def __init__(self) -> None:
        """Initializes the in-memory locking data store and thread mutex."""
        self._locks: dict[str, tuple[str, float]] = {}
        self._mutex = threading.Lock()

    def acquire(
        self,
        key: str,
        lease_duration: float,
        token: str,
        blocking: bool = False,  # pragma: no mutate
        timeout: float = 0.0,  # pragma: no mutate
    ) -> bool:
        """Acquires an in-memory lock.

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
        while True:
            with self._mutex:
                now = time.monotonic()
                # Clean up expired lock if any (self-healing / lease expiry logic)
                if key in self._locks:
                    _, expire_at = self._locks[key]
                    if now >= expire_at:
                        del self._locks[key]

                if key not in self._locks:
                    self._locks[key] = (token, now + lease_duration)
                    return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.01)

    def release(self, key: str, token: str) -> None:
        """Releases an in-memory lock if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        with self._mutex:
            if key in self._locks:
                held_token, _ = self._locks[key]
                # Invariant protection: Client can only release their own lock lease
                if held_token == token:
                    del self._locks[key]
