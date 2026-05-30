import re
from collections.abc import Callable
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os  # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException  # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit  # type: ignore
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


class AllowedHost(BaseModel):
    """Value Object representing a valid server host domain configuration."""

    host: str = Field(..., description="Allowed hostname or IP address")

    @field_validator("host")
    @classmethod
    def validate_hostname(cls, value: str) -> str:
        """Validate that the hostname conforms to standard RFC 1123 domain syntax."""
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("Hostname cannot be empty")

        # Basic validation for localhost, ipv4, and standard domain names
        domain_pattern = re.compile(
            r"^(localhost|([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,6}|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$"
        )
        if not domain_pattern.match(cleaned):
            raise ValueError(f"Invalid host syntax: '{value}'")

        return cleaned


class HttpResponseHeader(BaseModel):
    """Value Object encapsulating required security response headers."""

    x_frame_options: str = Field(default="DENY", alias="X-Frame-Options")
    x_content_type_options: str = Field(default="nosniff", alias="X-Content-Type-Options")
    strict_transport_security: str = Field(
        default="max-age=31536000; includeSubDomains; preload",
        alias="Strict-Transport-Security",
    )

    @field_validator("x_frame_options")
    @classmethod
    def validate_frame_options(cls, value: str) -> str:
        if value.upper() not in {"DENY", "SAMEORIGIN"}:
            raise ValueError("X-Frame-Options must be DENY or SAMEORIGIN")
        return value.upper()

    @field_validator("x_content_type_options")
    @classmethod
    def validate_content_type_options(cls, value: str) -> str:
        if value.lower() != "nosniff":
            raise ValueError("X-Content-Type-Options must be nosniff")
        return "nosniff"
