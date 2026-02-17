
from fastapi import APIRouter

from backend.app.api.v1.endpoints import search, health

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
