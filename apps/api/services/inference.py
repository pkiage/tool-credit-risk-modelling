"""Inference service for model predictions."""

import uuid
from datetime import datetime

import numpy as np

from apps.api.services.audit import emit_event
from apps.api.services.model_store import get_feature_columns, get_model
from shared import constants
from shared.logic.evaluation import calculate_model_confidence
from shared.logic.preprocessing import loan_application_to_feature_vector
from shared.schemas.audit import PredictionAuditEvent
from shared.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionResult,
)


def predict(request: PredictionRequest) -> PredictionResponse:
    """Make predictions for loan applications.

    Args:
        request: Prediction request with model ID and loan applications.

    Returns:
        Prediction response with results for all applications.

    Raises:
        ValueError: If model_id is not found.

    Example:
        >>> request = PredictionRequest(
        ...     model_id="model_123",
        ...     applications=[loan_app1, loan_app2]
        ... )
        >>> response = predict(request)
        >>> assert len(response.predictions) == 2
    """
    # Retrieve model
    stored_model = get_model(request.model_id)
    if stored_model is None:
        raise ValueError(f"Model not found: {request.model_id}")

    model = stored_model.model
    metadata = stored_model.metadata

    # Use specified threshold or model's optimal threshold
    if request.threshold is not None:
        threshold = request.threshold
    else:
        threshold = metadata.threshold

    # Convert applications to feature matrix, subsetting to model's training columns
    feature_columns = get_feature_columns(request.model_id)
    full_vectors = [
        loan_application_to_feature_vector(app) for app in request.applications
    ]
    if feature_columns is not None and feature_columns != constants.ALL_FEATURES:
        col_indices = [constants.ALL_FEATURES.index(c) for c in feature_columns]
        X = np.array(full_vectors)[:, col_indices]
    else:
        X = np.array(full_vectors)

    # Get predictions
    # Probability of default (class 1)
    y_proba = model.predict_proba(X)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    # Calculate confidence scores
    confidence_scores = calculate_model_confidence(y_proba, threshold)

    # Build prediction results
    predictions = [
        PredictionResult(
            application=app,
            predicted_default=bool(pred),
            default_probability=float(proba),
            confidence=float(conf),
        )
        for app, pred, proba, conf in zip(
            request.applications, y_pred, y_proba, confidence_scores
        )
    ]

    # Count predictions
    predicted_defaults = int(np.sum(y_pred == 1))
    predicted_approvals = int(np.sum(y_pred == 0))

    # Emit audit event
    audit_event = PredictionAuditEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        model_id=request.model_id,
        num_predictions=len(predictions),
        threshold_used=threshold,
        predicted_defaults=predicted_defaults,
        avg_default_probability=float(np.mean(y_proba)),
    )
    emit_event(audit_event)

    # Return prediction response
    return PredictionResponse(
        model_id=request.model_id,
        model_type=metadata.model_type,
        threshold=threshold,
        predictions=predictions,
        timestamp=datetime.now(),
        total_applications=len(predictions),
        predicted_defaults=predicted_defaults,
        predicted_approvals=predicted_approvals,
    )
