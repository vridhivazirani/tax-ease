"""GigSaathi Backend Configuration.

Loads all config from environment variables using pydantic-settings.
Never hardcode secrets — everything comes from .env or Cloud Run env vars.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # MongoDB Atlas
    MONGODB_URI: str = "mongodb://localhost:27017/gigsaathi"

    # Fivetran MCP (optional)
    FIVETRAN_API_KEY: str = ""
    FIVETRAN_API_SECRET: str = ""

    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Environment
    ENV: str = "development"

    # App constants
    FINANCIAL_YEAR: str = "2025-26"
    ASSESSMENT_YEAR: str = "2026-27"
    DB_NAME: str = "gigsaathi"

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 10
    MAX_FILES_PER_UPLOAD: int = 10

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

    @property
    def is_development(self) -> bool:
        return self.ENV == "development"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loaded once, reused everywhere."""
    return Settings()


# Convenience alias
settings = get_settings()
