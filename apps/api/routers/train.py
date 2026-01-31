"""Training endpoint router."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from apps.api.config import Settings
from apps.api.dependencies import get_settings
from apps.api.services.training import train_model
from shared.schemas.training import TrainingConfig, TrainingResult

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=TrainingResult)
async def train(
    config: TrainingConfig,
    settings: Settings = Depends(get_settings)
) -> TrainingResult:
    """Train a credit risk model.

    Args:
        config: Training configuration specifying model type and parameters.
        settings: Application settings (injected).

    Returns:
        TrainingResult with model ID, metrics, and optimal threshold.

    Raises:
        HTTPException: If training fails.

    Example Request:
        ```json
        {
            "model_type": "logistic_regression",
            "test_size": 0.2,
            "random_state": 42,
            "undersample": false,
            "cv_folds": 5
        }
        ```

    Example Response:
        ```json
        {
            "model_id": "model_a1b2c3d4",
            "model_type": "logistic_regression",
            "metrics": {
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.79,
                "f1_score": 0.80,
                "roc_auc": 0.88,
                "threshold_analysis": {
                    "threshold": 0.47,
                    "sensitivity": 0.79,
                    "specificity": 0.86,
                    "youden_j": 0.65,
                    "precision": 0.82,
                    "f1_score": 0.80
                },
                ...
            },
            "optimal_threshold": 0.47,
            "feature_importance": {"person_age": 0.05, ...},
            "training_config": {...}
        }
        ```
    """
    try:
        result = train_model(config, dataset_path=settings.default_dataset_path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {e}")
    except Exception:
        logger.exception("Training failed unexpectedly")
        raise HTTPException(status_code=500, detail="Internal server error")
