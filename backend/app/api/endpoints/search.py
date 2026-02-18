from fastapi import APIRouter
from backend.app.core.rag_service import RAGService
from backend.app.models.search import SearchRequest, SearchResponse

router = APIRouter()
_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


@router.post("", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Поиск с двухэтапной логикой."""
    rag = get_rag_service()

    results, llm_choice, processing_time = await rag.search(
        query=request.query,
        top_k=request.top_k,
        use_llm_analysis=request.use_llm_analysis,
    )

    return SearchResponse(
        results=results,
        llm_choice=llm_choice,
        query=request.query,
        total_found=len(results),
        processing_time_ms=round(processing_time, 2),
    )