"""Authentication endpoint router."""

from fastapi import APIRouter, Depends

from apps.api.auth import verify_api_key

router = APIRouter()


@router.post("/verify")
async def verify(
    api_key: str = Depends(verify_api_key),
) -> dict[str, str]:
    """Verify an API key.

    Args:
        api_key: Validated API key (injected).

    Returns:
        Status message confirming the key is valid.
    """
    return {"status": "valid", "message": "API key is valid"}
