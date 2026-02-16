from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Search query in natural language"
    )
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")
    min_confidence: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Minimum confidence threshold"
    )
    filters: Optional[dict[str, Any]] = Field(
        None,
        description="Optional filters: standard, armature, etc."
    )

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        return v.strip().replace("\x00", "")


class SearchResult(BaseModel):

    article: str = Field(..., description="Article number")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")

    confidence: float = Field(..., ge=0, le=1, description="Final confidence score")
    base_similarity: float = Field(..., ge=0, le=1, description="Semantic similarity")
    parameter_matches: List[str] = Field(
        default_factory=list,
        description="List of matched parameters"
    )

    extracted_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters extracted from query"
    )

    standard: Optional[str] = None
    thread: Optional[str] = None
    armature: Optional[str] = None
    angle: Optional[int] = None
    dy: Optional[int] = None
    price: Optional[float] = None


class SearchMetrics(BaseModel):
    total_results: int = 0
    processing_time_ms: float = 0.0
    extraction_time_ms: Optional[float] = None
    retrieval_time_ms: Optional[float] = None
    rerank_time_ms: Optional[float] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total_found: int
    metrics: SearchMetrics
    extracted_params: Optional[dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    services: dict[str, str] = Field(default_factory=dict)
    stats: dict[str, Any] = Field(default_factory=dict)
    uptime_seconds: Optional[float] = None