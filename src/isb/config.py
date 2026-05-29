from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    LANGFUSE_HOST: str = Field(default="https://cloud.langfuse.com", description="Langfuse cloud or self-hosted endpoint host")

    # Infrastructure routing ports
    API_PORT: int = Field(default=8000, description="Internal container port where Uvicorn serves the presentation API")


# Singleton configuration instance (Fail-fast validation on import)
settings = Settings()
