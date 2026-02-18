from backend.app.core.rag_service import RAGService
from backend.app.logging_config import get_logger

logger = get_logger("dependencies")

_rag_service: RAGService | None = None

def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

