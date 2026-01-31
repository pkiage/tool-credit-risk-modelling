"""Pytest fixtures for shared layer tests."""

import numpy as np
import pytest

from shared.schemas.loan import LoanApplication


@pytest.fixture
def sample_loan_application() -> LoanApplication:
    """Create a valid loan application for testing."""
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
        cb_person_default_on_file="N",
    )


@pytest.fixture
def sample_loan_applications() -> list[LoanApplication]:
    """Create a list of loan applications for testing."""
    return [
        LoanApplication(
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
            cb_person_default_on_file="N",
        ),
        LoanApplication(
            person_age=35,
            person_income=75000.0,
            person_emp_length=10.0,
            loan_amnt=20000.0,
            loan_int_rate=8.0,
            loan_percent_income=0.27,
            cb_person_cred_hist_length=12,
            person_home_ownership="OWN",
            loan_intent="HOMEIMPROVEMENT",
            loan_grade="A",
            cb_person_default_on_file="N",
        ),
        LoanApplication(
            person_age=45,
            person_income=100000.0,
            person_emp_length=20.0,
            loan_amnt=30000.0,
            loan_int_rate=12.0,
            loan_percent_income=0.3,
            cb_person_cred_hist_length=25,
            person_home_ownership="MORTGAGE",
            loan_intent="DEBTCONSOLIDATION",
            loan_grade="C",
            cb_person_default_on_file="Y",
        ),
    ]


@pytest.fixture
def binary_classification_data() -> tuple[np.ndarray, np.ndarray]:
    """Create binary classification test data.

    Returns:
        Tuple of (y_true, y_proba) with 20 samples.
    """
    # Create predictable test data
    y_true = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    y_proba = np.array(
        [
            0.1,
            0.15,
            0.2,
            0.25,
            0.3,
            0.35,
            0.4,
            0.45,
            0.5,
            0.55,
            0.5,
            0.55,
            0.6,
            0.65,
            0.7,
            0.75,
            0.8,
            0.85,
            0.9,
            0.95,
        ]
    )
    return y_true, y_proba


@pytest.fixture
def perfect_predictions() -> tuple[np.ndarray, np.ndarray]:
    """Create perfect prediction test data."""
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_proba = np.array([0.0, 0.1, 0.2, 0.3, 0.7, 0.8, 0.9, 1.0])
    return y_true, y_proba


@pytest.fixture
def imbalanced_data() -> tuple[np.ndarray, np.ndarray]:
    """Create imbalanced dataset for undersampling tests."""
    # 30 class 0 samples, 10 class 1 samples
    X = np.vstack(
        [np.random.randn(30, 5), np.random.randn(10, 5) + 2]  # Majority  # Minority
    )
    y = np.array([0] * 30 + [1] * 10)
    return X, y
