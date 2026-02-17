"""API dependencies."""

from fastapi import Header, HTTPException, Request, status

from backend.app.config import get_settings
from backend.app.core.rag_service import RAGService
from backend.app.exceptions import AuthenticationError, RateLimitExceeded
from backend.app.logging_config import get_logger

logger = get_logger("dependencies")

# Singleton services
_rag_service: RAGService | None = None
_auth_service = AuthService()
_rate_limit_service = RateLimitService()


def get_rag_service() -> RAGService:
    """Get or create RAG service singleton."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


async def verify_api_key(
        request: Request,
        x_api_key: str = Header(..., alias="X-API-Key"),
) -> str:
    """Verify API key header."""
    if not x_api_key:
        raise AuthenticationError("Missing API key")

    if not _auth_service.validate_api_key(x_api_key):
        raise AuthenticationError("Invalid API key")

    # Apply rate limiting per API key
    try:
        _rate_limit_service.check_rate_limit(
            identifier=x_api_key[:16],  # Use key prefix as identifier
            scope="api_key",
        )
    except RateLimitExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )

    return x_api_key


async def rate_limit(request: Request) -> dict:
    """Apply IP-based rate limiting."""
    client_ip = request.client.host if request.client else "unknown"

    try:
        return _rate_limit_service.check_rate_limit(
            identifier=client_ip,
            scope="ip",
        )
    except RateLimitExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )


async def verify_admin_key(x_admin_key: str = Header(..., alias="X-Admin-Key")) -> str:
    """Verify admin key for sensitive operations."""
    settings = get_settings()

    # Simple admin key from env
    expected = settings.jwt_secret  # or dedicated admin key

    if not x_admin_key or x_admin_key != expected:
        logger.warning("invalid_admin_attempt", key_prefix=x_admin_key[:8] if x_admin_key else None)
        raise HTTPException(403, "Invalid admin key")

    return x_admin_key