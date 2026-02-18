"""Health check."""

from fastapi import APIRouter, Depends
from backend.app.core.rag_service import RAGService
from backend.app.models.search import HealthResponse

router = APIRouter()

_rag_service: RAGService | None = None

def _get_rag_service():
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
        return _rag_service


@router.get("/health", response_model=HealthResponse)
async def health_check(rag_service: RAGService = Depends()):
    """Проверка здоровья сервиса."""
    try:
        rag_service = _get_rag_service()
        stats = rag_service.get_stats()
        return HealthResponse(
            status="healthy",
            version="2.0.0",
            environment="production",
            services={"chroma": "healthy", "embeddings": "healthy"},
            stats=stats,
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version="2.0.0",
            environment="production",
            services={"chroma": "error", "embeddings": "error", "error": str(e)},
            stats={},
        )