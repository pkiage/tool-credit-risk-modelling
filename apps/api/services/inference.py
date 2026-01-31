"""Inference service for model predictions."""

import uuid
from datetime import datetime

import numpy as np
from numpy.typing import NDArray

from apps.api.services.audit import emit_event
from apps.api.services.model_store import get_model
from shared.logic.evaluation import calculate_model_confidence
from shared.schemas.audit import PredictionAuditEvent
from shared.schemas.loan import LoanApplication
from shared.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionResult,
)


def loan_application_to_features(application: LoanApplication) -> NDArray[np.float64]:
    """Convert LoanApplication to feature vector.

    Args:
        application: Loan application with all required fields.

    Returns:
        Feature vector matching constants.ALL_FEATURES order.

    Example:
        >>> app = LoanApplication(
        ...     person_age=25,
        ...     person_income=50000.0,
        ...     person_emp_length=3.0,
        ...     loan_amnt=10000.0,
        ...     loan_int_rate=10.5,
        ...     loan_percent_income=0.2,
        ...     cb_person_cred_hist_length=5,
        ...     person_home_ownership="RENT",
        ...     loan_intent="EDUCATION",
        ...     loan_grade="B",
        ...     cb_person_default_on_file="N"
        ... )
        >>> features = loan_application_to_features(app)
        >>> assert features.shape == (27,)  # 7 numeric + 20 one-hot encoded
    """
    # Numeric features
    numeric_values = [
        float(application.person_age),
        float(application.person_income),
        float(application.person_emp_length),
        float(application.loan_amnt),
        float(application.loan_int_rate),
        float(application.loan_percent_income),
        float(application.cb_person_cred_hist_length),
    ]

    # One-hot encode categorical features
    # Home ownership
    home_ownership_encoded = [0.0] * 4  # MORTGAGE, OTHER, OWN, RENT
    home_map = {"MORTGAGE": 0, "OTHER": 1, "OWN": 2, "RENT": 3}
    home_ownership_encoded[home_map[application.person_home_ownership]] = 1.0

    # Loan intent
    loan_intent_encoded = [0.0] * 6  # DEBTCONSOLIDATION, EDUCATION, etc.
    intent_map = {
        "DEBTCONSOLIDATION": 0,
        "EDUCATION": 1,
        "HOMEIMPROVEMENT": 2,
        "MEDICAL": 3,
        "PERSONAL": 4,
        "VENTURE": 5,
    }
    loan_intent_encoded[intent_map[application.loan_intent]] = 1.0

    # Loan grade
    loan_grade_encoded = [0.0] * 7  # A, B, C, D, E, F, G
    grade_map = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6}
    loan_grade_encoded[grade_map[application.loan_grade]] = 1.0

    # Default on file
    default_encoded = [0.0, 0.0]  # N, Y
    default_map = {"N": 0, "Y": 1}
    default_encoded[default_map[application.cb_person_default_on_file]] = 1.0

    # Combine all features
    all_features = (
        numeric_values
        + home_ownership_encoded
        + loan_intent_encoded
        + loan_grade_encoded
        + default_encoded
    )

    return np.array(all_features, dtype=np.float64)


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

    # Convert applications to feature matrix
    X = np.array([
        loan_application_to_features(app)
        for app in request.applications
    ])

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
            confidence=float(conf)
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
        avg_default_probability=float(np.mean(y_proba))
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
        predicted_approvals=predicted_approvals
    )
