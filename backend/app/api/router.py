
from fastapi import APIRouter

from backend.app.api.endpoints import search

api_router = APIRouter()

api_router.include_router(search.router, prefix="/search", tags=["search"])

