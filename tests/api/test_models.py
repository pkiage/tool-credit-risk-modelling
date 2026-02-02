"""Tests for model management endpoints."""

from fastapi.testclient import TestClient

from shared.schemas.training import TrainingConfig


def test_list_models_empty(client: TestClient):
    """Test listing models when no models exist."""
    response = client.get("/models/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_models_after_training(
    client: TestClient, sample_training_config: TrainingConfig
):
    """Test listing models after training."""
    # Train a model
    train_response = client.post("/train/", json=sample_training_config.model_dump())
    assert train_response.status_code == 200
    model_id = train_response.json()["model_id"]

    # List models
    response = client.get("/models/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    model_metadata = data[0]
    assert model_metadata["model_id"] == model_id
    assert "model_type" in model_metadata
    assert "threshold" in model_metadata
    assert "roc_auc" in model_metadata
    assert "accuracy" in model_metadata
    assert "created_at" in model_metadata


def test_list_multiple_models(client: TestClient):
    """Test listing multiple models."""
    # Train multiple models
    config1 = TrainingConfig(model_type="logistic_regression")
    config2 = TrainingConfig(model_type="xgboost")

    client.post("/train/", json=config1.model_dump())
    client.post("/train/", json=config2.model_dump())

    # List models
    response = client.get("/models/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Verify different model types
    model_types = {model["model_type"] for model in data}
    assert "logistic_regression" in model_types
    assert "xgboost" in model_types


def test_get_model_metadata_success(
    client: TestClient, sample_training_config: TrainingConfig
):
    """Test getting metadata for a specific model."""
    # Train model
    train_response = client.post("/train/", json=sample_training_config.model_dump())
    model_id = train_response.json()["model_id"]

    # Get model metadata
    response = client.get(f"/models/{model_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == model_id
    assert data["model_type"] == "logistic_regression"
    assert 0 <= data["threshold"] <= 1
    assert 0 <= data["roc_auc"] <= 1
    assert 0 <= data["accuracy"] <= 1


def test_get_model_metadata_not_found(client: TestClient):
    """Test getting metadata for non-existent model."""
    response = client.get("/models/nonexistent_model")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_persist_model_success(
    client: TestClient, sample_training_config: TrainingConfig
):
    """Test persisting a model to disk."""
    # Train model
    train_response = client.post("/train/", json=sample_training_config.model_dump())
    model_id = train_response.json()["model_id"]

    # Persist model
    response = client.post(f"/models/{model_id}/persist")

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "model_id" in data
    assert "path" in data
    assert "instructions" in data

    assert data["model_id"] == model_id
    assert model_id in data["path"]
    assert ".joblib" in data["path"]
    assert "joblib" in data["instructions"].lower()
    assert "load" in data["instructions"].lower()


def test_persist_model_not_found(client: TestClient):
    """Test persisting a non-existent model."""
    response = client.post("/models/nonexistent_model/persist")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_model_workflow_integration(client: TestClient):
    """Test complete model workflow: train -> list -> get -> persist."""
    # Step 1: Train model
    config = TrainingConfig(model_type="xgboost")
    train_response = client.post("/train/", json=config.model_dump())
    assert train_response.status_code == 200
    model_id = train_response.json()["model_id"]

    # Step 2: List models
    list_response = client.get("/models/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    # Step 3: Get specific model
    get_response = client.get(f"/models/{model_id}")
    assert get_response.status_code == 200
    assert get_response.json()["model_id"] == model_id

    # Step 4: Persist model
    persist_response = client.post(f"/models/{model_id}/persist")
    assert persist_response.status_code == 200
    assert persist_response.json()["model_id"] == model_id
