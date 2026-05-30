from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
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


class Settings(BaseSettings):
    """Centralized configuration settings for the ISB.AI system.

    Uses Pydantic Settings (v2) to validate environment variables at startup,
    adhering to the fail-fast principle.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment and Debug
    ENV: str = Field(default="development", description="Current execution environment (development, testing, etc.)")
    DEBUG: bool = Field(default=True, description="Flag to enable/disable verbose logging and debug modes")

    # Storage and Databases
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/isb_dev",
        description="Database DSN string for PostgreSQL connection",
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Connection DSN for the Redis cache/broker instance",
    )

    # Langfuse Observability (SRE telemetry assertions)
    LANGFUSE_SECRET_KEY: str = Field(default="", description="Langfuse integration secret key")
    LANGFUSE_PUBLIC_KEY: str = Field(default="", description="Langfuse integration public key")
    LANGFUSE_HOST: str = Field(
        default="https://cloud.langfuse.com",
        description="Langfuse cloud or self-hosted endpoint host",
    )

    # Infrastructure routing ports
    API_PORT: int = Field(default=8000, description="Internal container port where Uvicorn serves the presentation API")


# Singleton configuration instance (Fail-fast validation on import)
settings = Settings()
