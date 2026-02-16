"""Health check endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends

from backend.app.api.v1.dependencies import get_rag_service
from backend.app.config import get_settings
from backend.app.core.rag_service import RAGService
from backend.app.models.search import HealthResponse

# Startup time for uptime calculation
START_TIME = datetime.now()

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def health_check(
        rag_service: RAGService = Depends(get_rag_service),
) -> HealthResponse:
    settings = get_settings()
    uptime = (datetime.now() - START_TIME).total_seconds()

    # Check services
    services = {
        "chroma": "healthy" if rag_service.chroma.count() > 0 else "empty",
        "embeddings": "healthy",
        "llm": "unknown",  # Could add ping
    }

    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        services=services,
        stats=rag_service.get_stats(),
        uptime_seconds=uptime,
    )


@router.get("/ready")
async def readiness_check(
        rag_service: RAGService = Depends(get_rag_service),
) -> dict:
    """Kubernetes readiness probe."""
    count = rag_service.chroma.count()
    if count == 0:
        return {"status": "not_ready", "reason": "empty_index"}
    return {"status": "ready", "articles": count}


@router.get("/live")
async def liveness_check() -> dict:
    """Kubernetes liveness probe."""
    return {"status": "alive"}