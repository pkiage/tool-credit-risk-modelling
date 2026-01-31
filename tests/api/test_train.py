"""Tests for training endpoint."""

from fastapi.testclient import TestClient

from shared.schemas.training import TrainingConfig


def test_train_model_success(client: TestClient, sample_training_config: TrainingConfig):
    """Test successful model training."""
    response = client.post("/train/", json=sample_training_config.model_dump())

    assert response.status_code == 200
    data = response.json()

    # Check required fields
    assert "model_id" in data
    assert "model_type" in data
    assert "metrics" in data
    assert "optimal_threshold" in data
    assert "training_config" in data

    # Verify model type
    assert data["model_type"] == "logistic_regression"

    # Verify metrics structure
    metrics = data["metrics"]
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1_score" in metrics
    assert "roc_auc" in metrics
    assert "threshold_analysis" in metrics

    # Verify threshold is valid
    threshold = data["optimal_threshold"]
    assert 0 <= threshold <= 1


def test_train_xgboost_model(client: TestClient):
    """Test training XGBoost model."""
    config = TrainingConfig(model_type="xgboost")
    response = client.post("/train/", json=config.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert data["model_type"] == "xgboost"
    assert "feature_importance" in data
    assert data["feature_importance"] is not None


def test_train_random_forest_model(client: TestClient):
    """Test training Random Forest model."""
    config = TrainingConfig(model_type="random_forest")
    response = client.post("/train/", json=config.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert data["model_type"] == "random_forest"
    assert "feature_importance" in data


def test_train_with_undersampling(client: TestClient):
    """Test training with undersampling enabled."""
    config = TrainingConfig(
        model_type="logistic_regression",
        undersample=True
    )
    response = client.post("/train/", json=config.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert data["training_config"]["undersample"] is True


def test_train_invalid_model_type(client: TestClient):
    """Test training with invalid model type."""
    invalid_config = {
        "model_type": "invalid_model",
        "test_size": 0.2,
        "random_state": 42
    }
    response = client.post("/train/", json=invalid_config)

    assert response.status_code == 422  # Validation error


def test_train_invalid_test_size(client: TestClient):
    """Test training with invalid test size."""
    invalid_config = {
        "model_type": "logistic_regression",
        "test_size": 0.9,  # Too large
        "random_state": 42
    }
    response = client.post("/train/", json=invalid_config)

    assert response.status_code == 422  # Validation error


def test_multiple_models_training(client: TestClient):
    """Test training multiple models in sequence."""
    config1 = TrainingConfig(model_type="logistic_regression")
    config2 = TrainingConfig(model_type="xgboost")

    response1 = client.post("/train/", json=config1.model_dump())
    response2 = client.post("/train/", json=config2.model_dump())

    assert response1.status_code == 200
    assert response2.status_code == 200

    model_id1 = response1.json()["model_id"]
    model_id2 = response2.json()["model_id"]

    # Ensure different model IDs
    assert model_id1 != model_id2
