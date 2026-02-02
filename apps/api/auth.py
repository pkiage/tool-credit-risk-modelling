"""API key authentication module."""

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from apps.api.config import Settings
from apps.api.dependencies import get_settings

API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(API_KEY_HEADER),
    settings: Settings = Depends(get_settings),
) -> str:
    """Verify the API key from the Authorization header.

    Allows bypass when ``settings.require_auth`` is ``False`` (dev mode).

    Args:
        api_key: Raw value of the Authorization header.
        settings: Application settings (injected).

    Returns:
        The validated API key token.

    Raises:
        HTTPException: 401 if the key is missing or invalid.
    """
    if not settings.require_auth:
        return "anonymous"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Strip "Bearer " prefix
    token = api_key.removeprefix("Bearer ")

    if token not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return token
