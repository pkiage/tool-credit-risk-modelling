"""In-memory model storage service."""

from typing import Any

from pydantic import BaseModel

from shared.schemas.model import ModelMetadata
from shared.schemas.training import TrainingResult

# In-memory model store (session-scoped, not persisted)
# In Phase 5, this will be replaced with persistent storage (filesystem, S3, MLflow)
_model_store: dict[str, dict[str, Any]] = {}


class StoredModel(BaseModel):
    """Complete stored model with metadata.

    Attributes:
        model: Trained sklearn/xgboost model object.
        metadata: Model metadata.
    """

    model: Any  # sklearn or xgboost model
    metadata: ModelMetadata

    model_config = {"arbitrary_types_allowed": True}


def store_model(
    model_id: str,
    model: Any,
    metadata: ModelMetadata,
    training_result: TrainingResult | None = None,
    feature_columns: list[str] | None = None,
) -> None:
    """Store a trained model in memory.

    Args:
        model_id: Unique identifier for the model.
        model: Trained model object (sklearn/xgboost).
        metadata: Model metadata.
        training_result: Full training result with metrics (optional).
        feature_columns: Ordered list of encoded column names the model was
            trained on. Required for prediction-time feature subsetting.

    Example:
        >>> from sklearn.linear_model import LogisticRegression
        >>> metadata = ModelMetadata(
        ...     model_id="model_123",
        ...     model_type="logistic_regression",
        ...     threshold=0.5,
        ...     roc_auc=0.85,
        ...     accuracy=0.82,
        ...     created_at="2025-01-31T00:00:00"
        ... )
        >>> store_model("model_123", LogisticRegression(), metadata)
    """
    _model_store[model_id] = {
        "model": model,
        "metadata": metadata.model_dump(),
        "training_result": training_result.model_dump() if training_result else None,
        "feature_columns": feature_columns,
    }


def get_model(model_id: str) -> StoredModel | None:
    """Retrieve a stored model by ID.

    Args:
        model_id: Model identifier to retrieve.

    Returns:
        StoredModel if found, None otherwise.

    Example:
        >>> stored = get_model("model_123")
        >>> if stored:
        ...     print(stored.metadata.model_type)
        logistic_regression
    """
    stored_data = _model_store.get(model_id)
    if stored_data is None:
        return None

    return StoredModel(
        model=stored_data["model"],
        metadata=ModelMetadata(**stored_data["metadata"]),
    )


def list_models() -> list[ModelMetadata]:
    """List all stored models' metadata.

    Returns:
        List of ModelMetadata for all stored models.

    Example:
        >>> models = list_models()
        >>> print(len(models))
        1
    """
    return [ModelMetadata(**stored["metadata"]) for stored in _model_store.values()]


def get_training_result(model_id: str) -> TrainingResult | None:
    """Retrieve stored training result for a model.

    Args:
        model_id: Model identifier.

    Returns:
        TrainingResult if stored, None if model not found or result not stored.
    """
    stored_data = _model_store.get(model_id)
    if stored_data is None or stored_data.get("training_result") is None:
        return None

    return TrainingResult(**stored_data["training_result"])


def get_feature_columns(model_id: str) -> list[str] | None:
    """Retrieve the feature columns a model was trained on.

    Args:
        model_id: Model identifier.

    Returns:
        List of encoded column names, or None if model not found.
    """
    stored_data = _model_store.get(model_id)
    if stored_data is None:
        return None
    return stored_data.get("feature_columns")


def delete_model(model_id: str) -> bool:
    """Delete a stored model.

    Args:
        model_id: Model identifier to delete.

    Returns:
        True if model was deleted, False if not found.
    """
    if model_id in _model_store:
        del _model_store[model_id]
        return True
    return False


def clear_all_models() -> None:
    """Clear all stored models.

    Used for testing and cleanup.
    """
    _model_store.clear()
