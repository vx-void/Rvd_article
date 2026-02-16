"""Search endpoint."""

from fastapi import APIRouter, Depends, Request

from backend.app.api.v1.dependencies import get_rag_service, verify_api_key, rate_limit
from backend.app.config import get_settings
from backend.app.core.rag_service import RAGService
from backend.app.logging_config import get_logger
from backend.app.models.search import SearchRequest, SearchResponse
from backend.app.services.metrics import MetricsService

logger = get_logger("api.search")
router = APIRouter()
metrics = MetricsService()


@router.post("", response_model=SearchResponse)
async def search(
        request: Request,
        search_request: SearchRequest,
        api_key: str = Depends(verify_api_key),
        rag_service: RAGService = Depends(get_rag_service),
        rate_limit_info: dict = Depends(rate_limit),
) -> SearchResponse:
    """
    Search hydraulic components.

    - **query**: Natural language description
    - **top_k**: Number of results (1-20)
    - **filters**: Optional filters (standard, armature, etc.)
    """

    client_ip = request.client.host if request.client else "unknown"

    logger.info(
        "search_request",
        query=search_request.query[:50],
        ip=client_ip,
        api_key_prefix=api_key[:8],
    )

    with metrics.track_search():
        response = await rag_service.search(search_request)

    return response


@router.post("/debug", response_model=SearchResponse, include_in_schema=False)
async def search_debug(
        search_request: SearchRequest,
        rag_service: RAGService = Depends(get_rag_service),
) -> SearchResponse:
    """Debug endpoint without auth (local only)."""
    settings = get_settings()
    if settings.environment == "production":
        raise HTTPException(403, "Debug disabled in production")

    return await rag_service.search(search_request)