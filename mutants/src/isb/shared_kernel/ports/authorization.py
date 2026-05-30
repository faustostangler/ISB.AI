from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator
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


class PermissionDeniedError(Exception):
    """Exception raised when a subject is unauthorized to perform an action on a resource."""
    pass


class Action(StrEnum):
    """Supported authorization action types for system resources."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    PURGE = "purge"


class Subject(BaseModel):
    """Value Object representing the entity requesting authorization."""

    user_id: str = Field(..., description="Unique user identifier")
    claims: dict[str, Any] = Field(default_factory=dict, description="Custom security claims and roles")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, value: str) -> str:
        """Enforce that the user ID is not empty or blank."""
        if not value or not value.strip():
            raise ValueError("User ID cannot be empty")
        return value.strip()


class Resource(BaseModel):
    """Value Object representing the target resource to authorize."""

    resource_id: str = Field(..., description="Unique resource identifier")
    resource_type: str = Field(..., description="Type classification of the resource")
    owner_id: str | None = Field(default=None, description="Optional owner identifier of the resource")

    @field_validator("resource_id", "resource_type")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        """Enforce that key identifiers are not empty or blank."""
        if not value or not value.strip():
            raise ValueError("Identifier fields cannot be empty")
        return value.strip()


class AuthorizationPort(ABC):
    """Abstract port defining the contract for executing access control decisions."""

    @abstractmethod
    def authorize(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Checks if the subject is authorized to perform the action on the resource.

        Args:
            subject: The requesting user identity.
            action: The requested action (read, write, delete, purge).
            resource: The target resource details.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # Step-by-step implementation walkthrough:
        # 1. Subject check: Validate user_id is present and clean.
        # 2. Check for Platform Admin role bypass in subject.claims.
        # 3. Compare resource.owner_id with subject.user_id for local ownership.
        # 4. Trigger security audit logging and metrics increment on access denial.
        raise NotImplementedError("Subclasses must implement the authorize method")

    def enforce(self, subject: Subject, action: Action, resource: Resource) -> None:
        args = [subject, action, resource]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁAuthorizationPortǁenforce__mutmut_orig'), object.__getattribute__(self, 'xǁAuthorizationPortǁenforce__mutmut_mutants'), args, kwargs, self)

    def xǁAuthorizationPortǁenforce__mutmut_orig(self, subject: Subject, action: Action, resource: Resource) -> None:
        """Enforces authorization, raising PermissionDeniedError if unauthorized.

        Args:
            subject: The requesting user identity.
            action: The requested action.
            resource: The target resource.

        Raises:
            PermissionDeniedError: If access is denied.
        """
        # Call authorize to evaluate rules
        if not self.authorize(subject, action, resource):
            # Raise the exception if authorize returns False
            raise PermissionDeniedError(
                f"Subject '{subject.user_id}' is not authorized to perform "
                f"'{action.value}' on resource '{resource.resource_id}' ({resource.resource_type})"
            )

    def xǁAuthorizationPortǁenforce__mutmut_1(self, subject: Subject, action: Action, resource: Resource) -> None:
        """Enforces authorization, raising PermissionDeniedError if unauthorized.

        Args:
            subject: The requesting user identity.
            action: The requested action.
            resource: The target resource.

        Raises:
            PermissionDeniedError: If access is denied.
        """
        # Call authorize to evaluate rules
        if self.authorize(subject, action, resource):
            # Raise the exception if authorize returns False
            raise PermissionDeniedError(
                f"Subject '{subject.user_id}' is not authorized to perform "
                f"'{action.value}' on resource '{resource.resource_id}' ({resource.resource_type})"
            )

    def xǁAuthorizationPortǁenforce__mutmut_2(self, subject: Subject, action: Action, resource: Resource) -> None:
        """Enforces authorization, raising PermissionDeniedError if unauthorized.

        Args:
            subject: The requesting user identity.
            action: The requested action.
            resource: The target resource.

        Raises:
            PermissionDeniedError: If access is denied.
        """
        # Call authorize to evaluate rules
        if not self.authorize(None, action, resource):
            # Raise the exception if authorize returns False
            raise PermissionDeniedError(
                f"Subject '{subject.user_id}' is not authorized to perform "
                f"'{action.value}' on resource '{resource.resource_id}' ({resource.resource_type})"
            )

    def xǁAuthorizationPortǁenforce__mutmut_3(self, subject: Subject, action: Action, resource: Resource) -> None:
        """Enforces authorization, raising PermissionDeniedError if unauthorized.

        Args:
            subject: The requesting user identity.
            action: The requested action.
            resource: The target resource.

        Raises:
            PermissionDeniedError: If access is denied.
        """
        # Call authorize to evaluate rules
        if not self.authorize(subject, None, resource):
            # Raise the exception if authorize returns False
            raise PermissionDeniedError(
                f"Subject '{subject.user_id}' is not authorized to perform "
                f"'{action.value}' on resource '{resource.resource_id}' ({resource.resource_type})"
            )

    def xǁAuthorizationPortǁenforce__mutmut_4(self, subject: Subject, action: Action, resource: Resource) -> None:
        """Enforces authorization, raising PermissionDeniedError if unauthorized.

        Args:
            subject: The requesting user identity.
            action: The requested action.
            resource: The target resource.

        Raises:
            PermissionDeniedError: If access is denied.
        """
        # Call authorize to evaluate rules
        if not self.authorize(subject, action, None):
            # Raise the exception if authorize returns False
            raise PermissionDeniedError(
                f"Subject '{subject.user_id}' is not authorized to perform "
                f"'{action.value}' on resource '{resource.resource_id}' ({resource.resource_type})"
            )

    def xǁAuthorizationPortǁenforce__mutmut_5(self, subject: Subject, action: Action, resource: Resource) -> None:
        """Enforces authorization, raising PermissionDeniedError if unauthorized.

        Args:
            subject: The requesting user identity.
            action: The requested action.
            resource: The target resource.

        Raises:
            PermissionDeniedError: If access is denied.
        """
        # Call authorize to evaluate rules
        if not self.authorize(action, resource):
            # Raise the exception if authorize returns False
            raise PermissionDeniedError(
                f"Subject '{subject.user_id}' is not authorized to perform "
                f"'{action.value}' on resource '{resource.resource_id}' ({resource.resource_type})"
            )

    def xǁAuthorizationPortǁenforce__mutmut_6(self, subject: Subject, action: Action, resource: Resource) -> None:
        """Enforces authorization, raising PermissionDeniedError if unauthorized.

        Args:
            subject: The requesting user identity.
            action: The requested action.
            resource: The target resource.

        Raises:
            PermissionDeniedError: If access is denied.
        """
        # Call authorize to evaluate rules
        if not self.authorize(subject, resource):
            # Raise the exception if authorize returns False
            raise PermissionDeniedError(
                f"Subject '{subject.user_id}' is not authorized to perform "
                f"'{action.value}' on resource '{resource.resource_id}' ({resource.resource_type})"
            )

    def xǁAuthorizationPortǁenforce__mutmut_7(self, subject: Subject, action: Action, resource: Resource) -> None:
        """Enforces authorization, raising PermissionDeniedError if unauthorized.

        Args:
            subject: The requesting user identity.
            action: The requested action.
            resource: The target resource.

        Raises:
            PermissionDeniedError: If access is denied.
        """
        # Call authorize to evaluate rules
        if not self.authorize(subject, action, ):
            # Raise the exception if authorize returns False
            raise PermissionDeniedError(
                f"Subject '{subject.user_id}' is not authorized to perform "
                f"'{action.value}' on resource '{resource.resource_id}' ({resource.resource_type})"
            )

    def xǁAuthorizationPortǁenforce__mutmut_8(self, subject: Subject, action: Action, resource: Resource) -> None:
        """Enforces authorization, raising PermissionDeniedError if unauthorized.

        Args:
            subject: The requesting user identity.
            action: The requested action.
            resource: The target resource.

        Raises:
            PermissionDeniedError: If access is denied.
        """
        # Call authorize to evaluate rules
        if not self.authorize(subject, action, resource):
            # Raise the exception if authorize returns False
            raise PermissionDeniedError(
                None
            )
    
    xǁAuthorizationPortǁenforce__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁAuthorizationPortǁenforce__mutmut_1': xǁAuthorizationPortǁenforce__mutmut_1, 
        'xǁAuthorizationPortǁenforce__mutmut_2': xǁAuthorizationPortǁenforce__mutmut_2, 
        'xǁAuthorizationPortǁenforce__mutmut_3': xǁAuthorizationPortǁenforce__mutmut_3, 
        'xǁAuthorizationPortǁenforce__mutmut_4': xǁAuthorizationPortǁenforce__mutmut_4, 
        'xǁAuthorizationPortǁenforce__mutmut_5': xǁAuthorizationPortǁenforce__mutmut_5, 
        'xǁAuthorizationPortǁenforce__mutmut_6': xǁAuthorizationPortǁenforce__mutmut_6, 
        'xǁAuthorizationPortǁenforce__mutmut_7': xǁAuthorizationPortǁenforce__mutmut_7, 
        'xǁAuthorizationPortǁenforce__mutmut_8': xǁAuthorizationPortǁenforce__mutmut_8
    }
    xǁAuthorizationPortǁenforce__mutmut_orig.__name__ = 'xǁAuthorizationPortǁenforce'
