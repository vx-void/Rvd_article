"""Поиск компонентов."""

from fastapi import APIRouter, Depends
from backend.app.core.rag_service import RAGService
from backend.app.models.search import SearchRequest, SearchResponse

router = APIRouter()


@router.post("", response_model=SearchResponse)
async def search(request: SearchRequest, rag_service: RAGService = Depends()):
    """Поиск гидравлических компонентов."""
    results, processing_time = rag_service.search(request.query, request.top_k)

    return SearchResponse(
        results=results,
        query=request.query,
        total_found=len(results),
        processing_time_ms=round(processing_time, 2),
    )