"""Health check."""

from fastapi import APIRouter, Depends
from backend.app.core.rag_service import RAGService
from backend.app.models.search import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(rag_service: RAGService = Depends()):
    """Проверка здоровья сервиса."""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        environment="production",
        services={"chroma": "healthy", "embeddings": "healthy"},
        stats=rag_service.get_stats(),
    )


@router.get("/ready")
async def readiness_check(rag_service: RAGService = Depends()):
    """Readiness probe."""
    count = rag_service.chroma.count()
    if count == 0:
        return {"status": "not_ready"}
    return {"status": "ready", "articles": count}

'''
@router.get("/live")
async def liveness_check():
    """Liveness probe."""
    return {"status": "alive"}
'''