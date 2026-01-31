"""Pytest fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient

from apps.api.config import Settings
from apps.api.main import create_app
from apps.api.services.model_store import clear_all_models
from shared.schemas.loan import LoanApplication
from shared.schemas.training import TrainingConfig


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        debug=True,
        default_dataset_path="data/processed/cr_loan_w2.csv",
        model_artifacts_path="test_artifacts/",
        log_level="DEBUG"
    )


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    """Create FastAPI test client.

    Args:
        test_settings: Test configuration settings.

    Returns:
        TestClient for making API requests.
    """
    app = create_app(settings=test_settings)
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_models():
    """Clear model store before each test."""
    clear_all_models()
    yield
    clear_all_models()


@pytest.fixture
def sample_training_config() -> TrainingConfig:
    """Create sample training configuration."""
    return TrainingConfig(
        model_type="logistic_regression",
        test_size=0.2,
        random_state=42,
        undersample=False,
        cv_folds=5
    )


@pytest.fixture
def sample_loan_application() -> LoanApplication:
    """Create sample loan application."""
    return LoanApplication(
        person_age=25,
        person_income=50000.0,
        person_emp_length=3.0,
        loan_amnt=10000.0,
        loan_int_rate=10.5,
        loan_percent_income=0.2,
        cb_person_cred_hist_length=5,
        person_home_ownership="RENT",
        loan_intent="EDUCATION",
        loan_grade="B",
        cb_person_default_on_file="N"
    )
