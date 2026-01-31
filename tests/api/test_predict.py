"""Tests for prediction endpoint."""

from fastapi.testclient import TestClient

from shared.schemas.loan import LoanApplication
from shared.schemas.training import TrainingConfig


def test_predict_success(
    client: TestClient,
    sample_training_config: TrainingConfig,
    sample_loan_application: LoanApplication
):
    """Test successful prediction."""
    # First train a model
    train_response = client.post("/train/", json=sample_training_config.model_dump())
    assert train_response.status_code == 200
    model_id = train_response.json()["model_id"]

    # Make prediction
    prediction_request = {
        "model_id": model_id,
        "applications": [sample_loan_application.model_dump()],
        "threshold": None,
        "include_probabilities": True
    }
    response = client.post("/predict/", json=prediction_request)

    assert response.status_code == 200
    data = response.json()

    # Check required fields
    assert "model_id" in data
    assert "model_type" in data
    assert "threshold" in data
    assert "predictions" in data
    assert "timestamp" in data
    assert "total_applications" in data
    assert "predicted_defaults" in data
    assert "predicted_approvals" in data

    # Verify predictions structure
    predictions = data["predictions"]
    assert len(predictions) == 1

    prediction = predictions[0]
    assert "application" in prediction
    assert "predicted_default" in prediction
    assert "default_probability" in prediction
    assert "confidence" in prediction

    # Verify probability and confidence are valid
    assert 0 <= prediction["default_probability"] <= 1
    assert 0 <= prediction["confidence"] <= 1


def test_predict_multiple_applications(
    client: TestClient,
    sample_training_config: TrainingConfig
):
    """Test prediction with multiple loan applications."""
    # Train model
    train_response = client.post("/train/", json=sample_training_config.model_dump())
    model_id = train_response.json()["model_id"]

    # Create multiple applications
    applications = [
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
            cb_person_default_on_file="N"
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
            cb_person_default_on_file="N"
        )
    ]

    prediction_request = {
        "model_id": model_id,
        "applications": [app.model_dump() for app in applications]
    }
    response = client.post("/predict/", json=prediction_request)

    assert response.status_code == 200
    data = response.json()
    assert len(data["predictions"]) == 2
    assert data["total_applications"] == 2


def test_predict_custom_threshold(
    client: TestClient,
    sample_training_config: TrainingConfig,
    sample_loan_application: LoanApplication
):
    """Test prediction with custom threshold."""
    # Train model
    train_response = client.post("/train/", json=sample_training_config.model_dump())
    model_id = train_response.json()["model_id"]

    # Predict with custom threshold
    prediction_request = {
        "model_id": model_id,
        "applications": [sample_loan_application.model_dump()],
        "threshold": 0.7  # Custom threshold
    }
    response = client.post("/predict/", json=prediction_request)

    assert response.status_code == 200
    data = response.json()
    assert data["threshold"] == 0.7


def test_predict_model_not_found(
    client: TestClient,
    sample_loan_application: LoanApplication
):
    """Test prediction with non-existent model."""
    prediction_request = {
        "model_id": "nonexistent_model",
        "applications": [sample_loan_application.model_dump()]
    }
    response = client.post("/predict/", json=prediction_request)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_predict_invalid_application(client: TestClient):
    """Test prediction with invalid loan application."""
    # Train model
    config = TrainingConfig(model_type="logistic_regression")
    train_response = client.post("/train/", json=config.model_dump())
    model_id = train_response.json()["model_id"]

    # Invalid application (missing required fields)
    prediction_request = {
        "model_id": model_id,
        "applications": [
            {
                "person_age": 25,
                "person_income": 50000.0
                # Missing other required fields
            }
        ]
    }
    response = client.post("/predict/", json=prediction_request)

    assert response.status_code == 422  # Validation error


def test_predict_empty_applications(client: TestClient):
    """Test prediction with empty applications list."""
    # Train model
    config = TrainingConfig(model_type="logistic_regression")
    train_response = client.post("/train/", json=config.model_dump())
    model_id = train_response.json()["model_id"]

    # Empty applications list
    prediction_request = {
        "model_id": model_id,
        "applications": []
    }
    response = client.post("/predict/", json=prediction_request)

    assert response.status_code == 422  # Validation error
