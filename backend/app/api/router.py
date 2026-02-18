
from fastapi import APIRouter

from backend.app.api.endpoints import health, search

api_router = APIRouter()

api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
