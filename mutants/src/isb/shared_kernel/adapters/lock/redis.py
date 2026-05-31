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


class RedisLockAdapter(LockPort):
    """Redis-based lease distributed lock adapter implementation of LockPort."""

    def __init__(self, redis_client: redis.Redis | None = None) -> None:
        args = [redis_client]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁRedisLockAdapterǁ__init____mutmut_orig'), object.__getattribute__(self, 'xǁRedisLockAdapterǁ__init____mutmut_mutants'), args, kwargs, self)

    def xǁRedisLockAdapterǁ__init____mutmut_orig(self, redis_client: redis.Redis | None = None) -> None:
        """Initializes the RedisLockAdapter.

        Args:
            redis_client: Optional pre-configured Redis client. If not provided,
                         a new client will be created from Settings.
        """
        if redis_client is not None:
            self._redis = redis_client
        else:
            self._redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def xǁRedisLockAdapterǁ__init____mutmut_1(self, redis_client: redis.Redis | None = None) -> None:
        """Initializes the RedisLockAdapter.

        Args:
            redis_client: Optional pre-configured Redis client. If not provided,
                         a new client will be created from Settings.
        """
        if redis_client is None:
            self._redis = redis_client
        else:
            self._redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def xǁRedisLockAdapterǁ__init____mutmut_2(self, redis_client: redis.Redis | None = None) -> None:
        """Initializes the RedisLockAdapter.

        Args:
            redis_client: Optional pre-configured Redis client. If not provided,
                         a new client will be created from Settings.
        """
        if redis_client is not None:
            self._redis = None
        else:
            self._redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def xǁRedisLockAdapterǁ__init____mutmut_3(self, redis_client: redis.Redis | None = None) -> None:
        """Initializes the RedisLockAdapter.

        Args:
            redis_client: Optional pre-configured Redis client. If not provided,
                         a new client will be created from Settings.
        """
        if redis_client is not None:
            self._redis = redis_client
        else:
            self._redis = None

    def xǁRedisLockAdapterǁ__init____mutmut_4(self, redis_client: redis.Redis | None = None) -> None:
        """Initializes the RedisLockAdapter.

        Args:
            redis_client: Optional pre-configured Redis client. If not provided,
                         a new client will be created from Settings.
        """
        if redis_client is not None:
            self._redis = redis_client
        else:
            self._redis = redis.Redis.from_url(None, decode_responses=True)

    def xǁRedisLockAdapterǁ__init____mutmut_5(self, redis_client: redis.Redis | None = None) -> None:
        """Initializes the RedisLockAdapter.

        Args:
            redis_client: Optional pre-configured Redis client. If not provided,
                         a new client will be created from Settings.
        """
        if redis_client is not None:
            self._redis = redis_client
        else:
            self._redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=None)

    def xǁRedisLockAdapterǁ__init____mutmut_6(self, redis_client: redis.Redis | None = None) -> None:
        """Initializes the RedisLockAdapter.

        Args:
            redis_client: Optional pre-configured Redis client. If not provided,
                         a new client will be created from Settings.
        """
        if redis_client is not None:
            self._redis = redis_client
        else:
            self._redis = redis.Redis.from_url(decode_responses=True)

    def xǁRedisLockAdapterǁ__init____mutmut_7(self, redis_client: redis.Redis | None = None) -> None:
        """Initializes the RedisLockAdapter.

        Args:
            redis_client: Optional pre-configured Redis client. If not provided,
                         a new client will be created from Settings.
        """
        if redis_client is not None:
            self._redis = redis_client
        else:
            self._redis = redis.Redis.from_url(settings.REDIS_URL, )

    def xǁRedisLockAdapterǁ__init____mutmut_8(self, redis_client: redis.Redis | None = None) -> None:
        """Initializes the RedisLockAdapter.

        Args:
            redis_client: Optional pre-configured Redis client. If not provided,
                         a new client will be created from Settings.
        """
        if redis_client is not None:
            self._redis = redis_client
        else:
            self._redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)
    
    xǁRedisLockAdapterǁ__init____mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁRedisLockAdapterǁ__init____mutmut_1': xǁRedisLockAdapterǁ__init____mutmut_1, 
        'xǁRedisLockAdapterǁ__init____mutmut_2': xǁRedisLockAdapterǁ__init____mutmut_2, 
        'xǁRedisLockAdapterǁ__init____mutmut_3': xǁRedisLockAdapterǁ__init____mutmut_3, 
        'xǁRedisLockAdapterǁ__init____mutmut_4': xǁRedisLockAdapterǁ__init____mutmut_4, 
        'xǁRedisLockAdapterǁ__init____mutmut_5': xǁRedisLockAdapterǁ__init____mutmut_5, 
        'xǁRedisLockAdapterǁ__init____mutmut_6': xǁRedisLockAdapterǁ__init____mutmut_6, 
        'xǁRedisLockAdapterǁ__init____mutmut_7': xǁRedisLockAdapterǁ__init____mutmut_7, 
        'xǁRedisLockAdapterǁ__init____mutmut_8': xǁRedisLockAdapterǁ__init____mutmut_8
    }
    xǁRedisLockAdapterǁ__init____mutmut_orig.__name__ = 'xǁRedisLockAdapterǁ__init__'

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
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁRedisLockAdapterǁacquire__mutmut_orig'), object.__getattribute__(self, 'xǁRedisLockAdapterǁacquire__mutmut_mutants'), args, kwargs, self)

    def xǁRedisLockAdapterǁacquire__mutmut_orig(
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

    def xǁRedisLockAdapterǁacquire__mutmut_1(
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
        start_time = None
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

    def xǁRedisLockAdapterǁacquire__mutmut_2(
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
        px_ms = None

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

    def xǁRedisLockAdapterǁacquire__mutmut_3(
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
        px_ms = int(None)

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

    def xǁRedisLockAdapterǁacquire__mutmut_4(
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
        px_ms = int(lease_duration / 1000)

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

    def xǁRedisLockAdapterǁacquire__mutmut_5(
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
        px_ms = int(lease_duration * 1001)

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

    def xǁRedisLockAdapterǁacquire__mutmut_6(
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

        while False:
            # Atomic acquisition via SET key token NX PX px_ms
            is_set = self._redis.set(key, token, nx=True, px=px_ms)
            if is_set:
                return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_7(
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
            is_set = None
            if is_set:
                return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_8(
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
            is_set = self._redis.set(None, token, nx=True, px=px_ms)
            if is_set:
                return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_9(
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
            is_set = self._redis.set(key, None, nx=True, px=px_ms)
            if is_set:
                return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_10(
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
            is_set = self._redis.set(key, token, nx=None, px=px_ms)
            if is_set:
                return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_11(
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
            is_set = self._redis.set(key, token, nx=True, px=None)
            if is_set:
                return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_12(
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
            is_set = self._redis.set(token, nx=True, px=px_ms)
            if is_set:
                return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_13(
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
            is_set = self._redis.set(key, nx=True, px=px_ms)
            if is_set:
                return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_14(
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
            is_set = self._redis.set(key, token, px=px_ms)
            if is_set:
                return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_15(
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
            is_set = self._redis.set(key, token, nx=True, )
            if is_set:
                return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_16(
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
            is_set = self._redis.set(key, token, nx=False, px=px_ms)
            if is_set:
                return True

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_17(
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
                return False

            if not blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_18(
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

            if blocking:
                return False

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_19(
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
                return True

            if time.monotonic() - start_time >= timeout:  # pragma: no mutate
                return False

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_20(
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
                return True

            time.sleep(0.05)

    def xǁRedisLockAdapterǁacquire__mutmut_21(
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

            time.sleep(None)

    def xǁRedisLockAdapterǁacquire__mutmut_22(
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

            time.sleep(1.05)
    
    xǁRedisLockAdapterǁacquire__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁRedisLockAdapterǁacquire__mutmut_1': xǁRedisLockAdapterǁacquire__mutmut_1, 
        'xǁRedisLockAdapterǁacquire__mutmut_2': xǁRedisLockAdapterǁacquire__mutmut_2, 
        'xǁRedisLockAdapterǁacquire__mutmut_3': xǁRedisLockAdapterǁacquire__mutmut_3, 
        'xǁRedisLockAdapterǁacquire__mutmut_4': xǁRedisLockAdapterǁacquire__mutmut_4, 
        'xǁRedisLockAdapterǁacquire__mutmut_5': xǁRedisLockAdapterǁacquire__mutmut_5, 
        'xǁRedisLockAdapterǁacquire__mutmut_6': xǁRedisLockAdapterǁacquire__mutmut_6, 
        'xǁRedisLockAdapterǁacquire__mutmut_7': xǁRedisLockAdapterǁacquire__mutmut_7, 
        'xǁRedisLockAdapterǁacquire__mutmut_8': xǁRedisLockAdapterǁacquire__mutmut_8, 
        'xǁRedisLockAdapterǁacquire__mutmut_9': xǁRedisLockAdapterǁacquire__mutmut_9, 
        'xǁRedisLockAdapterǁacquire__mutmut_10': xǁRedisLockAdapterǁacquire__mutmut_10, 
        'xǁRedisLockAdapterǁacquire__mutmut_11': xǁRedisLockAdapterǁacquire__mutmut_11, 
        'xǁRedisLockAdapterǁacquire__mutmut_12': xǁRedisLockAdapterǁacquire__mutmut_12, 
        'xǁRedisLockAdapterǁacquire__mutmut_13': xǁRedisLockAdapterǁacquire__mutmut_13, 
        'xǁRedisLockAdapterǁacquire__mutmut_14': xǁRedisLockAdapterǁacquire__mutmut_14, 
        'xǁRedisLockAdapterǁacquire__mutmut_15': xǁRedisLockAdapterǁacquire__mutmut_15, 
        'xǁRedisLockAdapterǁacquire__mutmut_16': xǁRedisLockAdapterǁacquire__mutmut_16, 
        'xǁRedisLockAdapterǁacquire__mutmut_17': xǁRedisLockAdapterǁacquire__mutmut_17, 
        'xǁRedisLockAdapterǁacquire__mutmut_18': xǁRedisLockAdapterǁacquire__mutmut_18, 
        'xǁRedisLockAdapterǁacquire__mutmut_19': xǁRedisLockAdapterǁacquire__mutmut_19, 
        'xǁRedisLockAdapterǁacquire__mutmut_20': xǁRedisLockAdapterǁacquire__mutmut_20, 
        'xǁRedisLockAdapterǁacquire__mutmut_21': xǁRedisLockAdapterǁacquire__mutmut_21, 
        'xǁRedisLockAdapterǁacquire__mutmut_22': xǁRedisLockAdapterǁacquire__mutmut_22
    }
    xǁRedisLockAdapterǁacquire__mutmut_orig.__name__ = 'xǁRedisLockAdapterǁacquire'

    def release(self, key: str, token: str) -> None:
        args = [key, token]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁRedisLockAdapterǁrelease__mutmut_orig'), object.__getattribute__(self, 'xǁRedisLockAdapterǁrelease__mutmut_mutants'), args, kwargs, self)

    def xǁRedisLockAdapterǁrelease__mutmut_orig(self, key: str, token: str) -> None:
        """Releases the lock via Redis atomically if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        # Execute safe Lua release script
        self._redis.eval(RELEASE_SCRIPT, 1, key, token)

    def xǁRedisLockAdapterǁrelease__mutmut_1(self, key: str, token: str) -> None:
        """Releases the lock via Redis atomically if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        # Execute safe Lua release script
        self._redis.eval(None, 1, key, token)

    def xǁRedisLockAdapterǁrelease__mutmut_2(self, key: str, token: str) -> None:
        """Releases the lock via Redis atomically if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        # Execute safe Lua release script
        self._redis.eval(RELEASE_SCRIPT, None, key, token)

    def xǁRedisLockAdapterǁrelease__mutmut_3(self, key: str, token: str) -> None:
        """Releases the lock via Redis atomically if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        # Execute safe Lua release script
        self._redis.eval(RELEASE_SCRIPT, 1, None, token)

    def xǁRedisLockAdapterǁrelease__mutmut_4(self, key: str, token: str) -> None:
        """Releases the lock via Redis atomically if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        # Execute safe Lua release script
        self._redis.eval(RELEASE_SCRIPT, 1, key, None)

    def xǁRedisLockAdapterǁrelease__mutmut_5(self, key: str, token: str) -> None:
        """Releases the lock via Redis atomically if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        # Execute safe Lua release script
        self._redis.eval(1, key, token)

    def xǁRedisLockAdapterǁrelease__mutmut_6(self, key: str, token: str) -> None:
        """Releases the lock via Redis atomically if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        # Execute safe Lua release script
        self._redis.eval(RELEASE_SCRIPT, key, token)

    def xǁRedisLockAdapterǁrelease__mutmut_7(self, key: str, token: str) -> None:
        """Releases the lock via Redis atomically if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        # Execute safe Lua release script
        self._redis.eval(RELEASE_SCRIPT, 1, token)

    def xǁRedisLockAdapterǁrelease__mutmut_8(self, key: str, token: str) -> None:
        """Releases the lock via Redis atomically if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        # Execute safe Lua release script
        self._redis.eval(RELEASE_SCRIPT, 1, key, )

    def xǁRedisLockAdapterǁrelease__mutmut_9(self, key: str, token: str) -> None:
        """Releases the lock via Redis atomically if the token matches.

        Args:
            key: The unique string identifying the locked resource.
            token: The unique identifier signature used to acquire the lock.
                   Only the holder of the correct token can release it.
        """
        # Execute safe Lua release script
        self._redis.eval(RELEASE_SCRIPT, 2, key, token)
    
    xǁRedisLockAdapterǁrelease__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁRedisLockAdapterǁrelease__mutmut_1': xǁRedisLockAdapterǁrelease__mutmut_1, 
        'xǁRedisLockAdapterǁrelease__mutmut_2': xǁRedisLockAdapterǁrelease__mutmut_2, 
        'xǁRedisLockAdapterǁrelease__mutmut_3': xǁRedisLockAdapterǁrelease__mutmut_3, 
        'xǁRedisLockAdapterǁrelease__mutmut_4': xǁRedisLockAdapterǁrelease__mutmut_4, 
        'xǁRedisLockAdapterǁrelease__mutmut_5': xǁRedisLockAdapterǁrelease__mutmut_5, 
        'xǁRedisLockAdapterǁrelease__mutmut_6': xǁRedisLockAdapterǁrelease__mutmut_6, 
        'xǁRedisLockAdapterǁrelease__mutmut_7': xǁRedisLockAdapterǁrelease__mutmut_7, 
        'xǁRedisLockAdapterǁrelease__mutmut_8': xǁRedisLockAdapterǁrelease__mutmut_8, 
        'xǁRedisLockAdapterǁrelease__mutmut_9': xǁRedisLockAdapterǁrelease__mutmut_9
    }
    xǁRedisLockAdapterǁrelease__mutmut_orig.__name__ = 'xǁRedisLockAdapterǁrelease'
