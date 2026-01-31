"""Schemas for model metadata and persistence."""

from pydantic import BaseModel


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


class PersistResponse(BaseModel):
    """Response from model persistence operation.

    Attributes:
        model_id: ID of the persisted model.
        path: File path where model was saved.
        instructions: Instructions for loading the model.
    """

    model_id: str
    path: str
    instructions: str
