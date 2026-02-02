"""Model management endpoint router."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from apps.api.auth import verify_api_key
from apps.api.config import Settings
from apps.api.dependencies import get_settings
from apps.api.services.model_store import get_model, get_training_result, list_models
from apps.api.services.persistent_model_store import PersistentModelStore
from shared.schemas.model import ModelMetadata, PersistResponse
from shared.schemas.training import TrainingResult

logger = logging.getLogger(__name__)

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
    """Persist a trained model to disk using joblib.

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
            "path": "artifacts/model_a1b2c3d4.joblib",
            "instructions": "Load with: import joblib; ..."
        }
        ```
    """
    stored_model = get_model(model_id)
    if stored_model is None:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")

    try:
        model_store = PersistentModelStore(base_path=settings.model_artifacts_path)
        path = model_store.save(
            model_id,
            stored_model.model,
            stored_model.metadata.model_dump(),
        )

        instructions = f"""
To load this model:

```python
import joblib, json

# Load model
model = joblib.load('{path}')

# Load metadata
with open('{path.replace(".joblib", ".json")}') as f:
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
            path=path,
            instructions=instructions,
        )

    except Exception:
        logger.exception("Failed to persist model %s", model_id)
        raise HTTPException(
            status_code=500,
            detail="Failed to persist model",
        )
