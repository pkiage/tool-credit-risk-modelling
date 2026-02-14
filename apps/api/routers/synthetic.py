"""Synthetic data generation endpoint router."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request

from apps.api.auth import verify_api_key
from apps.api.config import Settings
from apps.api.dependencies import get_settings
from apps.api.middleware.rate_limit import limiter
from apps.api.services.synthetic_store import store_dataset
from shared.logic.synthetic import generate_synthetic_dataset
from shared.schemas.synthetic import SyntheticConfig, SyntheticGenerateResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate/", response_model=SyntheticGenerateResponse)
@limiter.limit("20/hour")
async def generate_synthetic(
    request: Request,
    config: SyntheticConfig,
    settings: Settings = Depends(get_settings),
    _api_key: str = Depends(verify_api_key),
) -> SyntheticGenerateResponse:
    """Generate a synthetic credit risk dataset.

    Args:
        config: Synthetic generation configuration.

    Returns:
        SyntheticGenerateResponse with dataset_id and metadata.

    Raises:
        HTTPException: If generation fails.
    """
    try:
        X, y, feature_names, metadata = generate_synthetic_dataset(config)  # noqa: N806
        dataset_id = f"synth_{uuid.uuid4().hex[:8]}"
        store_dataset(dataset_id, X, y, feature_names, metadata)
        return SyntheticGenerateResponse(dataset_id=dataset_id, metadata=metadata)
    except ValueError as exc:
        logger.exception("Invalid synthetic generation config")
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        logger.exception("Synthetic generation failed")
        raise HTTPException(status_code=500, detail="Internal server error")
