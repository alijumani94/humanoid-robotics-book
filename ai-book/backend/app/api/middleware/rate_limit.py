"""Rate limiting middleware using SlowAPI."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.api_rate_limit_per_minute}/minute"]
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.

    Args:
        request: FastAPI request
        exc: RateLimitExceeded exception

    Returns:
        JSON error response
    """
    logger.warning(f"Rate limit exceeded for IP: {get_remote_address(request)}")

    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": "You're asking too many questions. Please wait a moment and try again.",
            "retry_after": exc.detail
        }
    )
