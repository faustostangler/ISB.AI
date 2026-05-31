import threading
import time

from isb.shared_kernel.ports.lock import LockPort
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


class InMemLockAdapter(LockPort):
    """In-memory thread-safe adapter implementation of the LockPort."""

    def __init__(self) -> None:
        args = []# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁInMemLockAdapterǁ__init____mutmut_orig'), object.__getattribute__(self, 'xǁInMemLockAdapterǁ__init____mutmut_mutants'), args, kwargs, self)

    def xǁInMemLockAdapterǁ__init____mutmut_orig(self) -> None:
        """Initializes the in-memory locking data store and thread mutex."""
        self._locks: dict[str, tuple[str, float]] = {}
        self._mutex = threading.Lock()

    def xǁInMemLockAdapterǁ__init____mutmut_1(self) -> None:
        """Initializes the in-memory locking data store and thread mutex."""
        self._locks: dict[str, tuple[str, float]] = None
        self._mutex = threading.Lock()

    def xǁInMemLockAdapterǁ__init____mutmut_2(self) -> None:
        """Initializes the in-memory locking data store and thread mutex."""
        self._locks: dict[str, tuple[str, float]] = {}
        self._mutex = None
    
    xǁInMemLockAdapterǁ__init____mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁInMemLockAdapterǁ__init____mutmut_1': xǁInMemLockAdapterǁ__init____mutmut_1, 
        'xǁInMemLockAdapterǁ__init____mutmut_2': xǁInMemLockAdapterǁ__init____mutmut_2
    }
    xǁInMemLockAdapterǁ__init____mutmut_orig.__name__ = 'xǁInMemLockAdapterǁ__init__'

    def acquire(
        self,
        key: str,
        lease_duration: float,
        token: str,
        blocking: bool = False,  # pragma: no mutate
        timeout: float = 0.0,  # pragma: no mutate
    ) -> bool:
        args = [key, lease_duration, token, blocking, timeout]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁInMemLockAdapterǁacquire__mutmut_orig'), object.__getattribute__(self, 'xǁInMemLockAdapterǁacquire__mutmut_mutants'), args, kwargs, self)

    def xǁInMemLockAdapterǁacquire__mutmut_orig(
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

    def xǁInMemLockAdapterǁacquire__mutmut_1(
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
        start_time = None
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

    def xǁInMemLockAdapterǁacquire__mutmut_2(
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
        while False:
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

    def xǁInMemLockAdapterǁacquire__mutmut_3(
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
                now = None
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

    def xǁInMemLockAdapterǁacquire__mutmut_4(
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
                if key not in self._locks:
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

    def xǁInMemLockAdapterǁacquire__mutmut_5(
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
                    _, expire_at = None
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

    def xǁInMemLockAdapterǁacquire__mutmut_6(
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
                    if now > expire_at:
                        del self._locks[key]

                if key not in self._locks:
                    self._locks[key] = (token, now + lease_duration)
                    return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.01)

    def xǁInMemLockAdapterǁacquire__mutmut_7(
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

                if key in self._locks:
                    self._locks[key] = (token, now + lease_duration)
                    return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.01)

    def xǁInMemLockAdapterǁacquire__mutmut_8(
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
                    self._locks[key] = None
                    return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.01)

    def xǁInMemLockAdapterǁacquire__mutmut_9(
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
                    self._locks[key] = (token, now - lease_duration)
                    return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.01)

    def xǁInMemLockAdapterǁacquire__mutmut_10(
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
                    return False

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.01)

    def xǁInMemLockAdapterǁacquire__mutmut_11(
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

            if blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.01)

    def xǁInMemLockAdapterǁacquire__mutmut_12(
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
                return True

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.01)

    def xǁInMemLockAdapterǁacquire__mutmut_13(
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
                return True

            time.sleep(0.01)

    def xǁInMemLockAdapterǁacquire__mutmut_14(
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

            time.sleep(None)

    def xǁInMemLockAdapterǁacquire__mutmut_15(
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

            time.sleep(1.01)
    
    xǁInMemLockAdapterǁacquire__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁInMemLockAdapterǁacquire__mutmut_1': xǁInMemLockAdapterǁacquire__mutmut_1, 
        'xǁInMemLockAdapterǁacquire__mutmut_2': xǁInMemLockAdapterǁacquire__mutmut_2, 
        'xǁInMemLockAdapterǁacquire__mutmut_3': xǁInMemLockAdapterǁacquire__mutmut_3, 
        'xǁInMemLockAdapterǁacquire__mutmut_4': xǁInMemLockAdapterǁacquire__mutmut_4, 
        'xǁInMemLockAdapterǁacquire__mutmut_5': xǁInMemLockAdapterǁacquire__mutmut_5, 
        'xǁInMemLockAdapterǁacquire__mutmut_6': xǁInMemLockAdapterǁacquire__mutmut_6, 
        'xǁInMemLockAdapterǁacquire__mutmut_7': xǁInMemLockAdapterǁacquire__mutmut_7, 
        'xǁInMemLockAdapterǁacquire__mutmut_8': xǁInMemLockAdapterǁacquire__mutmut_8, 
        'xǁInMemLockAdapterǁacquire__mutmut_9': xǁInMemLockAdapterǁacquire__mutmut_9, 
        'xǁInMemLockAdapterǁacquire__mutmut_10': xǁInMemLockAdapterǁacquire__mutmut_10, 
        'xǁInMemLockAdapterǁacquire__mutmut_11': xǁInMemLockAdapterǁacquire__mutmut_11, 
        'xǁInMemLockAdapterǁacquire__mutmut_12': xǁInMemLockAdapterǁacquire__mutmut_12, 
        'xǁInMemLockAdapterǁacquire__mutmut_13': xǁInMemLockAdapterǁacquire__mutmut_13, 
        'xǁInMemLockAdapterǁacquire__mutmut_14': xǁInMemLockAdapterǁacquire__mutmut_14, 
        'xǁInMemLockAdapterǁacquire__mutmut_15': xǁInMemLockAdapterǁacquire__mutmut_15
    }
    xǁInMemLockAdapterǁacquire__mutmut_orig.__name__ = 'xǁInMemLockAdapterǁacquire'

    def release(self, key: str, token: str) -> None:
        args = [key, token]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁInMemLockAdapterǁrelease__mutmut_orig'), object.__getattribute__(self, 'xǁInMemLockAdapterǁrelease__mutmut_mutants'), args, kwargs, self)

    def xǁInMemLockAdapterǁrelease__mutmut_orig(self, key: str, token: str) -> None:
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

    def xǁInMemLockAdapterǁrelease__mutmut_1(self, key: str, token: str) -> None:
        """Releases an in-memory lock if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        with self._mutex:
            if key not in self._locks:
                held_token, _ = self._locks[key]
                # Invariant protection: Client can only release their own lock lease
                if held_token == token:
                    del self._locks[key]

    def xǁInMemLockAdapterǁrelease__mutmut_2(self, key: str, token: str) -> None:
        """Releases an in-memory lock if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        with self._mutex:
            if key in self._locks:
                held_token, _ = None
                # Invariant protection: Client can only release their own lock lease
                if held_token == token:
                    del self._locks[key]

    def xǁInMemLockAdapterǁrelease__mutmut_3(self, key: str, token: str) -> None:
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
                if held_token != token:
                    del self._locks[key]
    
    xǁInMemLockAdapterǁrelease__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁInMemLockAdapterǁrelease__mutmut_1': xǁInMemLockAdapterǁrelease__mutmut_1, 
        'xǁInMemLockAdapterǁrelease__mutmut_2': xǁInMemLockAdapterǁrelease__mutmut_2, 
        'xǁInMemLockAdapterǁrelease__mutmut_3': xǁInMemLockAdapterǁrelease__mutmut_3
    }
    xǁInMemLockAdapterǁrelease__mutmut_orig.__name__ = 'xǁInMemLockAdapterǁrelease'
