from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


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
