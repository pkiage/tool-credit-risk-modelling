"""HTTP client for the Credit Risk API."""

from typing import Any

import httpx


class CreditRiskAPI:
    """Typed wrapper around the Credit Risk FastAPI endpoints.

    Attributes:
        base_url: Base URL of the running API server.
        client: httpx client with a 60s timeout (training can be slow).
        api_key: Optional API key for authenticated requests.
    """

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        """Initialize the API client.

        Args:
            base_url: Root URL of the FastAPI server.
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=60.0)
        self.api_key: str | None = None

    def set_api_key(self, key: str) -> None:
        """Set the API key for authenticated requests.

        Args:
            key: API key string.
        """
        self.api_key = key

    def _headers(self) -> dict[str, str]:
        """Build request headers including auth if available.

        Returns:
            Headers dictionary.
        """
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def train(self, config: dict[str, Any]) -> dict[str, Any]:
        """Train a credit risk model.

        Args:
            config: Training configuration matching TrainingConfig schema.

        Returns:
            TrainingResult as a dictionary.

        Raises:
            httpx.HTTPStatusError: If the API returns an error status.
        """
        response = self.client.post(
            f"{self.base_url}/train/", json=config, headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def predict(self, request: dict[str, Any]) -> dict[str, Any]:
        """Make predictions for loan applications.

        Args:
            request: Prediction request matching PredictionRequest schema.

        Returns:
            PredictionResponse as a dictionary.

        Raises:
            httpx.HTTPStatusError: If the API returns an error status.
        """
        response = self.client.post(
            f"{self.base_url}/predict/", json=request, headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def list_models(self) -> list[dict[str, Any]]:
        """List all trained models.

        Returns:
            List of ModelMetadata dictionaries.

        Raises:
            httpx.HTTPStatusError: If the API returns an error status.
        """
        response = self.client.get(f"{self.base_url}/models/", headers=self._headers())
        response.raise_for_status()
        return response.json()

    def get_model(self, model_id: str) -> dict[str, Any]:
        """Get metadata for a specific model.

        Args:
            model_id: Model identifier.

        Returns:
            ModelMetadata dictionary.

        Raises:
            httpx.HTTPStatusError: If the API returns an error status.
        """
        response = self.client.get(
            f"{self.base_url}/models/{model_id}", headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def get_model_results(self, model_id: str) -> dict[str, Any]:
        """Get full training results for a specific model.

        Args:
            model_id: Model identifier.

        Returns:
            TrainingResult dictionary with metrics, ROC curve, etc.

        Raises:
            httpx.HTTPStatusError: If the API returns an error status.
        """
        response = self.client.get(
            f"{self.base_url}/models/{model_id}/results", headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def verify_key(self) -> bool:
        """Verify the current API key against the auth endpoint.

        Returns:
            True if the key is valid, False otherwise.
        """
        try:
            response = self.client.post(
                f"{self.base_url}/auth/verify", headers=self._headers()
            )
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def health(self) -> bool:
        """Check if the API server is reachable.

        Returns:
            True if the health endpoint responds with 200, False otherwise.
        """
        try:
            response = self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except httpx.HTTPError:
            return False
