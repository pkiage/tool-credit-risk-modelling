"""Audit event schemas for compliance tracking."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    """Audit event for tracking model operations.

    Attributes:
        event_id: Unique identifier for the event.
        event_type: Type of event (training, prediction, evaluation).
        timestamp: When the event occurred.
        user_id: ID of user who triggered the event (if applicable).
        model_id: ID of model involved in the event (if applicable).
        metadata: Additional event-specific metadata.
        status: Status of the operation (success, failure, pending).
        error_message: Error message if status is failure.
    """

    event_id: str = Field(description="Unique event identifier")
    event_type: Literal["training", "prediction", "evaluation", "threshold_change"] = (
        Field(description="Type of audit event")
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Event timestamp"
    )
    user_id: str | None = Field(default=None, description="User who triggered event")
    model_id: str | None = Field(default=None, description="Related model ID")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Event-specific metadata"
    )
    status: Literal["success", "failure", "pending"] = Field(
        default="success", description="Operation status"
    )
    error_message: str | None = Field(
        default=None, description="Error details if failed"
    )


class TrainingAuditEvent(AuditEvent):
    """Audit event specific to model training.

    Attributes:
        model_type: Type of model trained.
        training_config: Configuration used for training.
        dataset_size: Number of samples in training dataset.
        test_accuracy: Final test accuracy achieved.
    """

    event_type: Literal["training"] = Field(default="training")
    model_type: str = Field(description="Type of model trained")
    training_config: dict[str, Any] = Field(description="Training configuration")
    dataset_size: int = Field(ge=0, description="Training dataset size")
    test_accuracy: float | None = Field(
        default=None, ge=0, le=1, description="Test accuracy"
    )


class PredictionAuditEvent(AuditEvent):
    """Audit event specific to predictions.

    Attributes:
        num_predictions: Number of predictions made.
        threshold_used: Classification threshold used.
        predicted_defaults: Number of predicted defaults.
        avg_default_probability: Average default probability across predictions.
    """

    event_type: Literal["prediction"] = Field(default="prediction")
    num_predictions: int = Field(ge=0, description="Number of predictions")
    threshold_used: float = Field(ge=0, le=1, description="Classification threshold")
    predicted_defaults: int = Field(ge=0, description="Number of predicted defaults")
    avg_default_probability: float = Field(
        ge=0, le=1, description="Average default probability"
    )


class ThresholdChangeAuditEvent(AuditEvent):
    """Audit event for threshold changes.

    Attributes:
        old_threshold: Previous threshold value.
        new_threshold: New threshold value.
        reason: Reason for threshold change.
        impact_metrics: Metrics showing impact of threshold change.
    """

    event_type: Literal["threshold_change"] = Field(default="threshold_change")
    old_threshold: float = Field(ge=0, le=1, description="Previous threshold")
    new_threshold: float = Field(ge=0, le=1, description="New threshold")
    reason: str = Field(description="Reason for change")
    impact_metrics: dict[str, float] = Field(
        default_factory=dict, description="Impact metrics"
    )
