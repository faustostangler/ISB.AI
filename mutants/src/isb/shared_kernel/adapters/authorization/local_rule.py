import logging

from prometheus_client import Counter

from isb.shared_kernel.ports.authorization import Action, AuthorizationPort, Resource, Subject

# Configure security audit logging
logger = logging.getLogger("isb.security")

# Prometheus Counter for tracking access control failures (Golden Signals: Errors)
AUTH_DENIALS_COUNTER = Counter(
    "isb_auth_denials_total",
    "Total number of authorization check denials",
    ["resource_type", "action"],
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


class LocalRuleAuthorizationAdapter(AuthorizationPort):
    """Adapter executing local rule-based attribute evaluation for authorization."""

    def __init__(self) -> None:
        """Initializes the adapter."""
        pass

    def authorize(self, subject: Subject, action: Action, resource: Resource) -> bool:
        args = [subject, action, resource]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_orig'), object.__getattribute__(self, 'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_mutants'), args, kwargs, self)

    def xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_orig(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning("Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s", action.value, resource.resource_id)  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate
            return False

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get("role") == "administrator":
            return True

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id == subject.user_id:
            return True

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning("Access Denied: Subject is not authorized. UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s", subject.user_id, action.value, resource.resource_id, resource.resource_type)  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate

        return False

    def xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_1(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning("Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s", action.value, resource.resource_id)  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate
            return True

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get("role") == "administrator":
            return True

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id == subject.user_id:
            return True

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning("Access Denied: Subject is not authorized. UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s", subject.user_id, action.value, resource.resource_id, resource.resource_type)  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate

        return False

    def xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_2(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning("Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s", action.value, resource.resource_id)  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate
            return False

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get(None) == "administrator":
            return True

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id == subject.user_id:
            return True

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning("Access Denied: Subject is not authorized. UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s", subject.user_id, action.value, resource.resource_id, resource.resource_type)  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate

        return False

    def xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_3(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning("Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s", action.value, resource.resource_id)  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate
            return False

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get("XXroleXX") == "administrator":
            return True

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id == subject.user_id:
            return True

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning("Access Denied: Subject is not authorized. UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s", subject.user_id, action.value, resource.resource_id, resource.resource_type)  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate

        return False

    def xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_4(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning("Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s", action.value, resource.resource_id)  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate
            return False

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get("ROLE") == "administrator":
            return True

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id == subject.user_id:
            return True

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning("Access Denied: Subject is not authorized. UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s", subject.user_id, action.value, resource.resource_id, resource.resource_type)  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate

        return False

    def xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_5(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning("Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s", action.value, resource.resource_id)  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate
            return False

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get("role") != "administrator":
            return True

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id == subject.user_id:
            return True

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning("Access Denied: Subject is not authorized. UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s", subject.user_id, action.value, resource.resource_id, resource.resource_type)  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate

        return False

    def xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_6(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning("Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s", action.value, resource.resource_id)  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate
            return False

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get("role") == "XXadministratorXX":
            return True

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id == subject.user_id:
            return True

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning("Access Denied: Subject is not authorized. UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s", subject.user_id, action.value, resource.resource_id, resource.resource_type)  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate

        return False

    def xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_7(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning("Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s", action.value, resource.resource_id)  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate
            return False

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get("role") == "ADMINISTRATOR":
            return True

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id == subject.user_id:
            return True

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning("Access Denied: Subject is not authorized. UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s", subject.user_id, action.value, resource.resource_id, resource.resource_type)  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate

        return False

    def xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_8(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning("Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s", action.value, resource.resource_id)  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate
            return False

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get("role") == "administrator":
            return False

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id == subject.user_id:
            return True

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning("Access Denied: Subject is not authorized. UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s", subject.user_id, action.value, resource.resource_id, resource.resource_type)  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate

        return False

    def xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_9(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning("Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s", action.value, resource.resource_id)  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate
            return False

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get("role") == "administrator":
            return True

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id != subject.user_id:
            return True

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning("Access Denied: Subject is not authorized. UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s", subject.user_id, action.value, resource.resource_id, resource.resource_type)  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate

        return False

    def xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_10(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning("Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s", action.value, resource.resource_id)  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate
            return False

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get("role") == "administrator":
            return True

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id == subject.user_id:
            return False

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning("Access Denied: Subject is not authorized. UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s", subject.user_id, action.value, resource.resource_id, resource.resource_type)  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate

        return False

    def xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_11(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning("Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s", action.value, resource.resource_id)  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate
            return False

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get("role") == "administrator":
            return True

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id == subject.user_id:
            return True

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning("Access Denied: Subject is not authorized. UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s", subject.user_id, action.value, resource.resource_id, resource.resource_type)  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(resource_type=resource.resource_type, action=action.value).inc()  # pragma: no mutate

        return True
    
    xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_1': xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_1, 
        'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_2': xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_2, 
        'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_3': xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_3, 
        'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_4': xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_4, 
        'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_5': xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_5, 
        'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_6': xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_6, 
        'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_7': xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_7, 
        'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_8': xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_8, 
        'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_9': xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_9, 
        'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_10': xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_10, 
        'xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_11': xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_11
    }
    xǁLocalRuleAuthorizationAdapterǁauthorize__mutmut_orig.__name__ = 'xǁLocalRuleAuthorizationAdapterǁauthorize'
