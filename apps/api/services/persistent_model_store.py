"""Persistent filesystem-based model storage service."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib


class PersistentModelStore:
    """Persist trained models to disk using joblib.

    Models are saved as ``.joblib`` files with companion ``.json`` metadata.

    Attributes:
        base_path: Directory where model artifacts are stored.
    """

    def __init__(self, base_path: str = "artifacts/models") -> None:
        """Initialize the persistent model store.

        Args:
            base_path: Directory path for model artifacts.
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, model_id: str, model: Any, metadata: dict[str, Any]) -> str:
        """Save a model and its metadata to disk.

        Args:
            model_id: Unique identifier for the model.
            model: Trained sklearn/xgboost model object.
            metadata: Model metadata dictionary.

        Returns:
            File path of the saved model.
        """
        model_path = self.base_path / f"{model_id}.joblib"
        meta_path = self.base_path / f"{model_id}.json"

        metadata["saved_at"] = datetime.now(tz=timezone.utc).isoformat()

        joblib.dump(model, model_path)
        meta_path.write_text(json.dumps(metadata, indent=2, default=str))

        return str(model_path)

    def load(self, model_id: str) -> tuple[Any, dict[str, Any]]:
        """Load a model and its metadata from disk.

        Args:
            model_id: Model identifier to load.

        Returns:
            Tuple of (model, metadata).

        Raises:
            FileNotFoundError: If the model file does not exist.
        """
        model_path = self.base_path / f"{model_id}.joblib"
        meta_path = self.base_path / f"{model_id}.json"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_id}")

        model = joblib.load(model_path)
        metadata: dict[str, Any] = (
            json.loads(meta_path.read_text()) if meta_path.exists() else {}
        )

        return model, metadata

    def list_models(self) -> list[dict[str, Any]]:
        """List all persisted models.

        Returns:
            List of metadata dictionaries for each persisted model.
        """
        models = []
        for meta_path in self.base_path.glob("*.json"):
            model_id = meta_path.stem
            metadata = json.loads(meta_path.read_text())
            models.append({"model_id": model_id, **metadata})
        return models

    def delete(self, model_id: str) -> bool:
        """Delete a persisted model.

        Args:
            model_id: Model identifier to delete.

        Returns:
            True if files were removed.
        """
        model_path = self.base_path / f"{model_id}.joblib"
        meta_path = self.base_path / f"{model_id}.json"

        if model_path.exists():
            model_path.unlink()
        if meta_path.exists():
            meta_path.unlink()

        return True
