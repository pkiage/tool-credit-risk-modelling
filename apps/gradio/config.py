"""Configuration for the Gradio stakeholder demo app."""

import os

API_BASE_URL: str = os.getenv("CREDIT_RISK_API_URL", "http://localhost:8000")
APP_TITLE: str = "Credit Risk Model Demo"
