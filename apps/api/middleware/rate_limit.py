"""Rate limiting configuration using SlowAPI."""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Handle rate limit exceeded errors.

    Args:
        request: The incoming request.
        exc: The rate limit exceeded exception.

    Returns:
        JSON response with 429 status code.
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "RATE_LIMIT_EXCEEDED",
            "message": f"Rate limit exceeded: {exc.detail}",
            "retry_after": str(exc.detail),
        },
    )
