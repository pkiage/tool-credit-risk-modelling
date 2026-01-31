"""Application configuration using pydantic-settings."""

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
    """

    app_name: str = "Credit Risk API"
    debug: bool = False
    default_dataset_path: str = "data/processed/cr_loan_w2.csv"
    model_artifacts_path: str = "artifacts/"
    log_level: str = "INFO"
    cors_origins: list[str] = ["*"]  # Allow all for dev, restrict in production

    model_config = SettingsConfigDict(env_prefix="CREDIT_RISK_")
