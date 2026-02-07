"""Training configuration and result schemas."""

from typing import Literal

from pydantic import BaseModel, Field

from shared.schemas.metrics import ModelMetrics


class TrainingConfig(BaseModel):
    """Configuration for model training.

    Attributes:
        model_type: Type of ML model to train.
        test_size: Fraction of data reserved for testing (0.1-0.5).
        random_state: Random seed for reproducibility.
        undersample: Whether to undersample the majority class for imbalanced data.
        cv_folds: Number of cross-validation folds (2-10).
        selected_features: Encoded column names to train on. None = all features.
    """

    model_type: Literal["logistic_regression", "xgboost", "random_forest"] = Field(
        description="ML model type"
    )
    test_size: float = Field(
        default=0.2, ge=0.1, le=0.5, description="Test set fraction"
    )
    random_state: int = Field(default=42, description="Random seed for reproducibility")
    undersample: bool = Field(default=False, description="Undersample majority class")
    cv_folds: int = Field(default=5, ge=2, le=10, description="CV folds")
    selected_features: list[str] | None = Field(
        default=None,
        description="Encoded column names to train on. None = all features.",
    )


class TrainingResult(BaseModel):
    """Result of model training including metrics and artifacts.

    Attributes:
        model_id: Unique identifier for the trained model.
        model_type: Type of ML model that was trained.
        metrics: Performance metrics on test set.
        optimal_threshold: Optimal classification threshold based on Youden's J.
        feature_importance: Feature importance scores (None for models without this).
        training_config: Configuration used for training.
        training_time_seconds: Wall-clock time for model training in seconds.
    """

    model_id: str = Field(description="Unique model identifier")
    model_type: str = Field(description="Model type")
    metrics: ModelMetrics = Field(description="Model performance metrics")
    optimal_threshold: float = Field(
        ge=0, le=1, description="Optimal classification threshold"
    )
    feature_importance: dict[str, float] | None = Field(
        default=None, description="Feature importance scores"
    )
    training_config: TrainingConfig = Field(description="Training configuration")
    training_time_seconds: float = Field(
        ge=0, description="Wall-clock training time in seconds"
    )
