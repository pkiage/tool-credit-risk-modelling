"""Configuration for the Gradio stakeholder demo app."""

import logging
import os

logger = logging.getLogger(__name__)

API_BASE_URL: str = os.getenv("CREDIT_RISK_API_URL", "http://localhost:8000")
APP_TITLE: str = "Credit Risk Model Demo"

# Warn if API URL is not HTTPS in non-localhost environments
if not API_BASE_URL.startswith("https://") and "localhost" not in API_BASE_URL:
    logger.warning(
        "CREDIT_RISK_API_URL is not using HTTPS (%s). "
        "Use HTTPS in production to protect API keys in transit.",
        API_BASE_URL,
    )
