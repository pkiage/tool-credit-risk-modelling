"""Tests for the feature selection API endpoint."""

from fastapi.testclient import TestClient


class TestFeatureSelectionEndpoint:
    """Tests for POST /feature-selection/."""

    def test_tree_importance(self, client: TestClient) -> None:
        """Tree importance endpoint returns expected structure."""
        response = client.post(
            "/feature-selection/",
            json={
                "method": "tree_importance",
                "tree_params": {"model_type": "random_forest", "top_k": 10},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["method"] == "tree_importance"
        assert data["n_selected"] == 10
        assert data["n_total"] == 26
        assert len(data["feature_scores"]) == 26

    def test_lasso(self, client: TestClient) -> None:
        """LASSO endpoint returns non-zero selections."""
        response = client.post(
            "/feature-selection/",
            json={"method": "lasso", "lasso_params": {"C": 1.0}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["method"] == "lasso"
        assert data["n_selected"] > 0

    def test_woe_iv(self, client: TestClient) -> None:
        """WoE/IV endpoint returns IV metadata."""
        response = client.post(
            "/feature-selection/",
            json={
                "method": "woe_iv",
                "woe_iv_params": {"n_bins": 10, "iv_threshold": 0.1},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["method"] == "woe_iv"
        assert "mean_iv" in data["method_metadata"]

    def test_boruta(self, client: TestClient) -> None:
        """Boruta endpoint classifies features."""
        response = client.post(
            "/feature-selection/",
            json={
                "method": "boruta",
                "boruta_params": {"n_iterations": 20},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["method"] == "boruta"
        assert "n_confirmed" in data["method_metadata"]

    def test_shap(self, client: TestClient) -> None:
        """SHAP endpoint returns SHAP-based selection."""
        response = client.post(
            "/feature-selection/",
            json={
                "method": "shap",
                "shap_params": {"model_type": "xgboost", "top_k": 10},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["method"] == "shap"
        assert data["n_selected"] == 10

    def test_invalid_method(self, client: TestClient) -> None:
        """Invalid method returns 422."""
        response = client.post(
            "/feature-selection/",
            json={"method": "nonexistent"},
        )
        assert response.status_code == 422

    def test_default_params(self, client: TestClient) -> None:
        """Method with no explicit params uses defaults."""
        response = client.post(
            "/feature-selection/",
            json={"method": "tree_importance"},
        )
        assert response.status_code == 200
        data = response.json()
        # Defaults: no top_k, no threshold → selects all non-zero
        assert data["n_total"] == 26
