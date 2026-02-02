"""Application configuration using pydantic-settings."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API configuration settings.

    Attributes:
        app_name: Application name.
        debug: Enable debug mode.
        default_dataset_path: Path to default training dataset.
        model_artifacts_path: Directory for persisted model artifacts.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        cors_origins: List of allowed CORS origins.
        require_auth: Whether API key authentication is required.
        api_keys: List of valid API keys.
    """

    app_name: str = "Credit Risk API"
    debug: bool = False
    default_dataset_path: str = "data/processed/cr_loan_w2.csv"
    model_artifacts_path: str = "artifacts/"
    log_level: str = "INFO"
    cors_origins: list[str] = ["*"]

    # Auth
    require_auth: bool = False  # Default off for dev
    api_keys: list[str] = []

    model_config = SettingsConfigDict(env_prefix="CREDIT_RISK_")

    @field_validator("api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v: str | list[str]) -> list[str]:
        """Parse comma-separated API keys from environment variable."""
        if isinstance(v, str):
            return [k.strip() for k in v.split(",") if k.strip()]
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse comma-separated CORS origins from environment variable."""
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v
