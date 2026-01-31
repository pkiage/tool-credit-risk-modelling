"""Prediction endpoint router."""

import logging

from fastapi import APIRouter, HTTPException

from apps.api.services.inference import predict
from shared.schemas.prediction import PredictionRequest, PredictionResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=PredictionResponse)
async def make_predictions(request: PredictionRequest) -> PredictionResponse:
    """Make predictions for loan applications.

    Args:
        request: Prediction request with model ID and loan applications.

    Returns:
        PredictionResponse with predictions for all applications.

    Raises:
        HTTPException: If model not found or prediction fails.

    Example Request:
        ```json
        {
            "model_id": "model_a1b2c3d4",
            "applications": [
                {
                    "person_age": 25,
                    "person_income": 50000.0,
                    "person_emp_length": 3.0,
                    "loan_amnt": 10000.0,
                    "loan_int_rate": 10.5,
                    "loan_percent_income": 0.2,
                    "cb_person_cred_hist_length": 5,
                    "person_home_ownership": "RENT",
                    "loan_intent": "EDUCATION",
                    "loan_grade": "B",
                    "cb_person_default_on_file": "N"
                }
            ],
            "threshold": null,
            "include_probabilities": true
        }
        ```

    Example Response:
        ```json
        {
            "model_id": "model_a1b2c3d4",
            "model_type": "logistic_regression",
            "threshold": 0.47,
            "predictions": [
                {
                    "application": {...},
                    "predicted_default": false,
                    "default_probability": 0.25,
                    "confidence": 0.47
                }
            ],
            "timestamp": "2025-01-31T00:00:00",
            "total_applications": 1,
            "predicted_defaults": 0,
            "predicted_approvals": 1
        }
        ```
    """
    try:
        response = predict(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.exception("Prediction failed unexpectedly")
        raise HTTPException(status_code=500, detail="Internal server error")
