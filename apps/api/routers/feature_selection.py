"""Feature selection endpoint router."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from apps.api.auth import verify_api_key
from apps.api.config import Settings
from apps.api.dependencies import get_settings
from apps.api.middleware.rate_limit import limiter
from apps.api.services.feature_selection_service import run_feature_selection
from shared.schemas.feature_selection import (
    FeatureSelectionRequest,
    FeatureSelectionResult,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=FeatureSelectionResult)
@limiter.limit("20/hour")
def select_features(
    request: Request,
    fs_request: FeatureSelectionRequest,
    settings: Settings = Depends(get_settings),
    _api_key: str = Depends(verify_api_key),
) -> FeatureSelectionResult:
    """Run automatic feature selection on the training dataset.

    Supports 5 methods: tree_importance, lasso, woe_iv, boruta, shap.

    Args:
        request: FastAPI request object (for rate limiting).
        fs_request: Feature selection configuration.
        settings: Application settings (injected).

    Returns:
        FeatureSelectionResult with selected features and scores.

    Raises:
        HTTPException: If feature selection fails.
    """
    try:
        return run_feature_selection(
            fs_request, dataset_path=settings.default_dataset_path
        )
    except FileNotFoundError:
        logger.exception("Dataset not found during feature selection")
        raise HTTPException(status_code=404, detail="Dataset not found")
    except ValueError as exc:
        logger.exception("Invalid feature selection configuration")
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        logger.exception("Feature selection failed unexpectedly")
        raise HTTPException(status_code=500, detail="Internal server error")
