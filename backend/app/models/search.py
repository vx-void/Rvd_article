"""Модели данных."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ExtractedParams(BaseModel):
    """Извлеченные параметры."""
    standard: Optional[str] = None
    thread: Optional[str] = None
    armature: Optional[str] = None
    angle: Optional[int] = None
    dy: Optional[int] = None
    component_type: Optional[str] = None
    confidence: str = "medium"


class SearchResult(BaseModel):
    """Результат поиска."""
    article: str
    name: str
    description: Optional[str] = None
    confidence: float
    base_similarity: float
    parameter_matches: List[str] = Field(default_factory=list)
    extracted_params: Dict[str, Any] = Field(default_factory=dict)
    standard: Optional[str] = None
    thread: Optional[str] = None
    armature: Optional[str] = None
    angle: Optional[int] = None
    dy: Optional[int] = None
    price: Optional[float] = None


class SearchRequest(BaseModel):
    """Запрос на поиск."""
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)


class SearchResponse(BaseModel):
    """Ответ на поиск."""
    results: List[SearchResult]
    query: str
    total_found: int
    processing_time_ms: float


class HealthResponse(BaseModel):
    """Health check."""
    status: str
    version: str
    environment: str
    services: Dict[str, str]
    stats: Dict[str, Any]