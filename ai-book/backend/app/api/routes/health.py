"""Health check endpoint."""

from fastapi import APIRouter
from app.models.schemas import HealthCheckResponse
from app.services.db_service import check_db_health
from app.services.retrieval_service import check_qdrant_health
from app.services.agent_service import check_openai_health
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Check health status of all services.

    Returns:
        HealthCheckResponse with status of each service
    """
    services = {}

    # Check database
    try:
        db_healthy = await check_db_health()
        services["database"] = "connected" if db_healthy else "disconnected"
    except Exception as e:
        logger.error(f"Database health check error: {e}")
        services["database"] = "error"

    # Check Qdrant
    try:
        qdrant_healthy = await check_qdrant_health()
        services["qdrant"] = "connected" if qdrant_healthy else "disconnected"
    except Exception as e:
        logger.error(f"Qdrant health check error: {e}")
        services["qdrant"] = "error"

    # Check OpenAI
    try:
        openai_healthy = await check_openai_health()
        services["openai"] = "connected" if openai_healthy else "disconnected"
    except Exception as e:
        logger.error(f"OpenAI health check error: {e}")
        services["openai"] = "error"

    # Determine overall status
    all_healthy = all(status == "connected" for status in services.values())
    overall_status = "healthy" if all_healthy else "degraded"

    return HealthCheckResponse(
        status=overall_status,
        services=services,
        timestamp=datetime.utcnow()
    )
