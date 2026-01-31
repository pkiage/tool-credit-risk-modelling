"""FastAPI dependency injection providers."""

from functools import lru_cache

from apps.api.config import Settings


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Application settings loaded from environment.

    Example:
        >>> settings = get_settings()
        >>> assert settings.app_name == "Credit Risk API"
    """
    return Settings()
