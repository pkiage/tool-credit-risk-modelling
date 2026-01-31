"""In-memory model storage service."""

from typing import Any

from pydantic import BaseModel

# In-memory model store (session-scoped, not persisted)
# In Phase 5, this will be replaced with persistent storage (filesystem, S3, MLflow)
_model_store: dict[str, dict[str, Any]] = {}


class ModelMetadata(BaseModel):
    """Metadata for a stored model.

    Attributes:
        model_id: Unique identifier for the model.
        model_type: Type of ML model (logistic_regression, xgboost, random_forest).
        threshold: Optimal classification threshold.
        roc_auc: Area under ROC curve.
        accuracy: Test set accuracy.
        created_at: Timestamp when model was trained.
    """

    model_id: str
    model_type: str
    threshold: float
    roc_auc: float
    accuracy: float
    created_at: str


class StoredModel(BaseModel):
    """Complete stored model with metadata.

    Attributes:
        model: Trained sklearn/xgboost model object.
        metadata: Model metadata.
    """

    model: Any  # sklearn or xgboost model
    metadata: ModelMetadata

    model_config = {"arbitrary_types_allowed": True}


def store_model(model_id: str, model: Any, metadata: ModelMetadata) -> None:
    """Store a trained model in memory.

    Args:
        model_id: Unique identifier for the model.
        model: Trained model object (sklearn/xgboost).
        metadata: Model metadata.

    Example:
        >>> from sklearn.linear_model import LogisticRegression
        >>> model = LogisticRegression()
        >>> metadata = ModelMetadata(
        ...     model_id="model_123",
        ...     model_type="logistic_regression",
        ...     threshold=0.5,
        ...     roc_auc=0.85,
        ...     accuracy=0.82,
        ...     created_at="2025-01-31T00:00:00"
        ... )
        >>> store_model("model_123", model, metadata)
    """
    _model_store[model_id] = {
        "model": model,
        "metadata": metadata.model_dump(),
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
    return [
        ModelMetadata(**stored["metadata"])
        for stored in _model_store.values()
    ]


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
