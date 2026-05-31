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
from typing import Annotated
from typing import Callable
from typing import ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit # type: ignore
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__) # type: ignore
        # (for class methods, orig is bound and thus does not need the explicit self argument)
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_' # type: ignore
    if not mutant_under_test.startswith(prefix): # type: ignore
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    mutant_name = mutant_under_test.rpartition('.')[-1] # type: ignore
    if self_arg is not None: # type: ignore
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs) # type: ignore
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs) # type: ignore
    return result # type: ignore


def _extract_lock_prefix(key: str) -> str:
    args = [key]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x__extract_lock_prefix__mutmut_orig, x__extract_lock_prefix__mutmut_mutants, args, kwargs, None)


def x__extract_lock_prefix__mutmut_orig(key: str) -> str:
    """Helper to extract the base prefix from a lock key string.

    E.g., "lock:scrape:url:123" -> "lock:scrape:url"
    If no colon is present, returns the key itself.
    """
    parts = key.split(":")
    if len(parts) > 1:
        return ":".join(parts[:-1])
    return key


def x__extract_lock_prefix__mutmut_1(key: str) -> str:
    """Helper to extract the base prefix from a lock key string.

    E.g., "lock:scrape:url:123" -> "lock:scrape:url"
    If no colon is present, returns the key itself.
    """
    parts = None
    if len(parts) > 1:
        return ":".join(parts[:-1])
    return key


def x__extract_lock_prefix__mutmut_2(key: str) -> str:
    """Helper to extract the base prefix from a lock key string.

    E.g., "lock:scrape:url:123" -> "lock:scrape:url"
    If no colon is present, returns the key itself.
    """
    parts = key.split(None)
    if len(parts) > 1:
        return ":".join(parts[:-1])
    return key


def x__extract_lock_prefix__mutmut_3(key: str) -> str:
    """Helper to extract the base prefix from a lock key string.

    E.g., "lock:scrape:url:123" -> "lock:scrape:url"
    If no colon is present, returns the key itself.
    """
    parts = key.split("XX:XX")
    if len(parts) > 1:
        return ":".join(parts[:-1])
    return key


def x__extract_lock_prefix__mutmut_4(key: str) -> str:
    """Helper to extract the base prefix from a lock key string.

    E.g., "lock:scrape:url:123" -> "lock:scrape:url"
    If no colon is present, returns the key itself.
    """
    parts = key.split(":")
    if len(parts) >= 1:
        return ":".join(parts[:-1])
    return key


def x__extract_lock_prefix__mutmut_5(key: str) -> str:
    """Helper to extract the base prefix from a lock key string.

    E.g., "lock:scrape:url:123" -> "lock:scrape:url"
    If no colon is present, returns the key itself.
    """
    parts = key.split(":")
    if len(parts) > 2:
        return ":".join(parts[:-1])
    return key


def x__extract_lock_prefix__mutmut_6(key: str) -> str:
    """Helper to extract the base prefix from a lock key string.

    E.g., "lock:scrape:url:123" -> "lock:scrape:url"
    If no colon is present, returns the key itself.
    """
    parts = key.split(":")
    if len(parts) > 1:
        return ":".join(None)
    return key


def x__extract_lock_prefix__mutmut_7(key: str) -> str:
    """Helper to extract the base prefix from a lock key string.

    E.g., "lock:scrape:url:123" -> "lock:scrape:url"
    If no colon is present, returns the key itself.
    """
    parts = key.split(":")
    if len(parts) > 1:
        return "XX:XX".join(parts[:-1])
    return key


def x__extract_lock_prefix__mutmut_8(key: str) -> str:
    """Helper to extract the base prefix from a lock key string.

    E.g., "lock:scrape:url:123" -> "lock:scrape:url"
    If no colon is present, returns the key itself.
    """
    parts = key.split(":")
    if len(parts) > 1:
        return ":".join(parts[:+1])
    return key


def x__extract_lock_prefix__mutmut_9(key: str) -> str:
    """Helper to extract the base prefix from a lock key string.

    E.g., "lock:scrape:url:123" -> "lock:scrape:url"
    If no colon is present, returns the key itself.
    """
    parts = key.split(":")
    if len(parts) > 1:
        return ":".join(parts[:-2])
    return key

x__extract_lock_prefix__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x__extract_lock_prefix__mutmut_1': x__extract_lock_prefix__mutmut_1, 
    'x__extract_lock_prefix__mutmut_2': x__extract_lock_prefix__mutmut_2, 
    'x__extract_lock_prefix__mutmut_3': x__extract_lock_prefix__mutmut_3, 
    'x__extract_lock_prefix__mutmut_4': x__extract_lock_prefix__mutmut_4, 
    'x__extract_lock_prefix__mutmut_5': x__extract_lock_prefix__mutmut_5, 
    'x__extract_lock_prefix__mutmut_6': x__extract_lock_prefix__mutmut_6, 
    'x__extract_lock_prefix__mutmut_7': x__extract_lock_prefix__mutmut_7, 
    'x__extract_lock_prefix__mutmut_8': x__extract_lock_prefix__mutmut_8, 
    'x__extract_lock_prefix__mutmut_9': x__extract_lock_prefix__mutmut_9
}
x__extract_lock_prefix__mutmut_orig.__name__ = 'x__extract_lock_prefix'


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
