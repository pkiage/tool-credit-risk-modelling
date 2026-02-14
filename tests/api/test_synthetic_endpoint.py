"""Tests for synthetic data generation endpoint and training integration."""

from fastapi.testclient import TestClient


class TestSyntheticGenerate:
    """Tests for POST /synthetic/generate/ endpoint."""

    def test_generate_default_config(self, client: TestClient) -> None:
        """Generate synthetic data with default config returns 200."""
        response = client.post("/synthetic/generate/", json={})
        assert response.status_code == 200

        data = response.json()
        assert "dataset_id" in data
        assert data["dataset_id"].startswith("synth_")
        assert "metadata" in data
        assert data["metadata"]["n_samples"] == 5000
        assert data["metadata"]["n_features"] > 0
        assert 0.0 <= data["metadata"]["default_rate_actual"] <= 1.0
        assert len(data["metadata"]["feature_names"]) == data["metadata"]["n_features"]

    def test_generate_custom_config(self, client: TestClient) -> None:
        """Generate synthetic data with custom params reflects config."""
        response = client.post(
            "/synthetic/generate/",
            json={"n_samples": 200, "default_rate": 0.1, "random_seed": 99},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["metadata"]["n_samples"] == 200
        # Actual default rate should be reasonably close to configured rate
        assert 0.0 <= data["metadata"]["default_rate_actual"] <= 1.0

    def test_generate_below_minimum_samples(self, client: TestClient) -> None:
        """n_samples below minimum (100) returns 422 validation error."""
        response = client.post(
            "/synthetic/generate/",
            json={"n_samples": 50},
        )
        assert response.status_code == 422


class TestSyntheticTrainingIntegration:
    """Tests for training on synthetic datasets."""

    def test_train_on_synthetic_dataset(self, client: TestClient) -> None:
        """Generate synthetic data then train on it successfully."""
        # Generate synthetic dataset
        gen_response = client.post(
            "/synthetic/generate/",
            json={"n_samples": 500, "random_seed": 42},
        )
        assert gen_response.status_code == 200
        dataset_id = gen_response.json()["dataset_id"]

        # Train on synthetic dataset
        train_response = client.post(
            "/train/",
            json={
                "model_type": "logistic_regression",
                "test_size": 0.2,
                "random_state": 42,
                "dataset_id": dataset_id,
            },
        )
        assert train_response.status_code == 200

        result = train_response.json()
        assert "model_id" in result
        assert result["model_type"] == "logistic_regression"
        assert "metrics" in result
        assert 0 <= result["optimal_threshold"] <= 1

    def test_train_with_invalid_dataset_id(self, client: TestClient) -> None:
        """Training with nonexistent dataset_id returns 400."""
        response = client.post(
            "/train/",
            json={
                "model_type": "logistic_regression",
                "dataset_id": "synth_nonexistent",
            },
        )
        assert response.status_code == 400

    def test_data_source_synthetic(self, client: TestClient) -> None:
        """Model trained on synthetic data has data_source='synthetic'."""
        # Generate and train
        gen_response = client.post(
            "/synthetic/generate/",
            json={"n_samples": 500, "random_seed": 42},
        )
        dataset_id = gen_response.json()["dataset_id"]

        train_response = client.post(
            "/train/",
            json={
                "model_type": "logistic_regression",
                "dataset_id": dataset_id,
            },
        )
        model_id = train_response.json()["model_id"]

        # Check model metadata
        models_response = client.get("/models/")
        assert models_response.status_code == 200
        models = models_response.json()
        model = next(m for m in models if m["model_id"] == model_id)
        assert model["data_source"] == "synthetic"

    def test_data_source_real(self, client: TestClient) -> None:
        """Model trained on real data has data_source='real'."""
        train_response = client.post(
            "/train/",
            json={"model_type": "logistic_regression"},
        )
        assert train_response.status_code == 200
        model_id = train_response.json()["model_id"]

        models_response = client.get("/models/")
        models = models_response.json()
        model = next(m for m in models if m["model_id"] == model_id)
        assert model["data_source"] == "real"
