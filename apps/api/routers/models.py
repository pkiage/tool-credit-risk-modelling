"""Model management endpoint router."""

import json
import pickle
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from apps.api.auth import verify_api_key
from apps.api.config import Settings
from apps.api.dependencies import get_settings
from apps.api.services.model_store import get_model, get_training_result, list_models
from shared.schemas.model import ModelMetadata, PersistResponse
from shared.schemas.training import TrainingResult

router = APIRouter()


@router.get("/", response_model=list[ModelMetadata])
async def get_models() -> list[ModelMetadata]:
    """List all trained models in session.

    Returns:
        List of model metadata for all stored models.

    Example Response:
        ```json
        [
            {
                "model_id": "model_a1b2c3d4",
                "model_type": "logistic_regression",
                "threshold": 0.47,
                "roc_auc": 0.88,
                "accuracy": 0.85,
                "created_at": "2025-01-31T00:00:00"
            }
        ]
        ```
    """
    return list_models()


@router.get("/{model_id}", response_model=ModelMetadata)
async def get_model_metadata(model_id: str) -> ModelMetadata:
    """Get metadata for a specific model.

    Args:
        model_id: Model identifier.

    Returns:
        Model metadata.

    Raises:
        HTTPException: If model not found.
    """
    stored_model = get_model(model_id)
    if stored_model is None:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")

    return stored_model.metadata


@router.get("/{model_id}/results", response_model=TrainingResult)
async def get_model_results(model_id: str) -> TrainingResult:
    """Get full training results for a stored model.

    Args:
        model_id: Model identifier.

    Returns:
        Full training result including metrics, ROC curve, confusion matrix, etc.

    Raises:
        HTTPException: If model not found or training results not available.
    """
    stored_model = get_model(model_id)
    if stored_model is None:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")

    result = get_training_result(model_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Training results not available for model: {model_id}",
        )

    return result


@router.post("/{model_id}/persist", response_model=PersistResponse)
async def persist_model(
    model_id: str,
    settings: Settings = Depends(get_settings),
    _api_key: str = Depends(verify_api_key),
) -> PersistResponse:
    """Persist a trained model to disk.

    Args:
        model_id: Model identifier to persist.
        settings: Application settings (injected).

    Returns:
        PersistResponse with file path and loading instructions.

    Raises:
        HTTPException: If model not found or persistence fails.

    Example Response:
        ```json
        {
            "model_id": "model_a1b2c3d4",
            "path": "artifacts/model_a1b2c3d4.pkl",
            "instructions": "Load with: import pickle; ..."
        }
        ```
    """
    # Retrieve model
    stored_model = get_model(model_id)
    if stored_model is None:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")

    try:
        # Create artifacts directory if it doesn't exist
        artifacts_dir = Path(settings.model_artifacts_path)
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Save model
        model_path = artifacts_dir / f"{model_id}.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(stored_model.model, f)

        # Save metadata
        metadata_path = artifacts_dir / f"{model_id}_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(stored_model.metadata.model_dump(), f, indent=2, default=str)

        # Generate loading instructions
        instructions = f"""
To load this model:

```python
import pickle

# Load model
with open('{model_path}', 'rb') as f:
    model = pickle.load(f)

# Load metadata
import json
with open('{metadata_path}', 'r') as f:
    metadata = json.load(f)

# Make predictions
import numpy as np
X_new = np.array([...])  # Your feature matrix
y_proba = model.predict_proba(X_new)[:, 1]
threshold = metadata['threshold']
predictions = (y_proba >= threshold).astype(int)
```
        """.strip()

        return PersistResponse(
            model_id=model_id,
            path=str(model_path),
            instructions=instructions
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to persist model: {e}"
        )
