"""Admin endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.v1.dependencies import verify_admin_key
from backend.app.config import get_settings
from backend.app.core.cache import SearchCache
from backend.app.core.indexer import IndexManager
from backend.app.logging_config import get_logger
from backend.app.services.auth import AuthService

logger = get_logger("api.admin")
router = APIRouter()


@router.post("/reindex")
async def reindex(
        admin_key: str = Depends(verify_admin_key),
        clear: bool = True,
):
    """Rebuild search index."""
    settings = get_settings()

    if not settings.articles_file.exists():
        raise HTTPException(404, "Articles file not found")

    indexer = IndexManager()
    count = await indexer.index_from_json(settings.articles_file, clear_existing=clear)

    # Clear cache after reindex
    SearchCache().clear()

    logger.warning("index_rebuilt", admin_key_prefix=admin_key[:8], count=count)

    return {"status": "success", "indexed": count}


@router.get("/stats")
async def get_stats(
        admin_key: str = Depends(verify_admin_key),
        rag_service=Depends(lambda: None),  # Will be injected properly
):
    """Get system statistics."""
    # Implementation depends on dependency injection setup
    pass


@router.post("/api-keys")
async def create_api_key(
        admin_key: str = Depends(verify_admin_key),
        name: str = "default",
):
    """Generate new API key."""
    new_key = AuthService.generate_api_key()
    return {
        "key": new_key,
        "name": name,
        "created_at": "now",
        "important": "SAVE THIS KEY - it won't be shown again",
    }