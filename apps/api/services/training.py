"""Model training service."""

import time
import uuid
from datetime import datetime

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from apps.api.services.audit import emit_event
from apps.api.services.model_store import store_model
from shared import constants
from shared.logic.evaluation import evaluate_model
from shared.logic.preprocessing import undersample_majority_class
from shared.schemas.audit import TrainingAuditEvent
from shared.schemas.model import ModelMetadata
from shared.schemas.training import TrainingConfig, TrainingResult


def load_dataset_from_csv(
    filepath: str,
) -> tuple[NDArray[np.float64], NDArray[np.int_]]:
    """Load dataset from CSV file.

    Args:
        filepath: Path to CSV file.

    Returns:
        Tuple of (X, y) where X is feature matrix and y is target labels.

    Raises:
        FileNotFoundError: If CSV file doesn't exist.
        ValueError: If required columns are missing.
    """
    df = pd.read_csv(filepath)

    # Validate required columns exist
    if constants.TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Target column '{constants.TARGET_COLUMN}' not found in dataset"
        )

    missing_features = [f for f in constants.ALL_FEATURES if f not in df.columns]
    if missing_features:
        raise ValueError(f"Missing feature columns: {missing_features}")

    # Extract features and target
    X = df[constants.ALL_FEATURES].values.astype(np.float64)
    y = df[constants.TARGET_COLUMN].values.astype(np.int_)

    return X, y


def create_model(
    model_type: str,
) -> LogisticRegression | XGBClassifier | RandomForestClassifier:
    """Create sklearn/xgboost model instance.

    Args:
        model_type: Type of model to create.

    Returns:
        Untrained model instance.

    Raises:
        ValueError: If model_type is not recognized.
    """
    if model_type == "logistic_regression":
        return LogisticRegression(**constants.LOGISTIC_REGRESSION_PARAMS)  # type: ignore[arg-type]  # dict unpacking
    elif model_type == "xgboost":
        return XGBClassifier(**constants.XGBOOST_PARAMS)  # type: ignore[arg-type]  # dict unpacking
    elif model_type == "random_forest":
        return RandomForestClassifier(**constants.RANDOM_FOREST_PARAMS)  # type: ignore[arg-type]  # dict unpacking
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def train_model(
    config: TrainingConfig, dataset_path: str | None = None
) -> TrainingResult:
    """Train a credit risk model.

    Args:
        config: Training configuration.
        dataset_path: Path to dataset CSV. If None, uses default.

    Returns:
        TrainingResult with metrics and model ID.

    Raises:
        FileNotFoundError: If dataset file doesn't exist.
        ValueError: If configuration is invalid.

    Example:
        >>> config = TrainingConfig(model_type="logistic_regression")
        >>> result = train_model(config, "data/raw/cr_loan_w2.csv")
        >>> assert result.model_id
        >>> assert 0 <= result.optimal_threshold <= 1
    """
    # Generate descriptive model ID: type, test size, unique suffix
    test_pct = int(config.test_size * 100)
    model_id = f"{config.model_type}_test{test_pct}_{uuid.uuid4().hex[:6]}"
    timestamp = datetime.now().isoformat()

    # Load dataset
    if dataset_path is None:
        dataset_path = "data/processed/cr_loan_w2.csv"

    X, y = load_dataset_from_csv(dataset_path)

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.test_size, random_state=config.random_state, stratify=y
    )

    # Undersample if requested
    if config.undersample:
        X_train, y_train = undersample_majority_class(
            X_train, y_train, random_state=config.random_state
        )

    # Create and train model
    t_start = time.monotonic()
    model = create_model(config.model_type)
    model.fit(X_train, y_train)
    training_time_seconds = time.monotonic() - t_start

    # Get predictions on test set
    y_proba = model.predict_proba(X_test)[:, 1]  # Probability of default (class 1)

    # Evaluate model using shared logic
    metrics = evaluate_model(y_test, y_proba)

    # Extract feature importance if available
    feature_importance: dict[str, float] | None = None
    if hasattr(model, "feature_importances_"):
        feature_importance = {
            feature: float(importance)
            for feature, importance in zip(
                constants.ALL_FEATURES, model.feature_importances_
            )
        }

    # Store model in memory
    metadata = ModelMetadata(
        model_id=model_id,
        model_type=config.model_type,
        threshold=metrics.threshold_analysis.threshold,
        roc_auc=metrics.roc_auc,
        accuracy=metrics.accuracy,
        created_at=timestamp,
    )

    # Build training result
    training_result = TrainingResult(
        model_id=model_id,
        model_type=config.model_type,
        metrics=metrics,
        optimal_threshold=metrics.threshold_analysis.threshold,
        feature_importance=feature_importance,
        training_config=config,
        training_time_seconds=round(training_time_seconds, 3),
    )

    store_model(model_id, model, metadata, training_result=training_result)

    # Emit audit event
    audit_event = TrainingAuditEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        model_id=model_id,
        model_type=config.model_type,
        training_config=config.model_dump(),
        dataset_size=len(X),
        test_accuracy=metrics.accuracy,
    )
    emit_event(audit_event)

    return training_result
