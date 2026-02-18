from typing import Optional, List
from pydantic import BaseModel, Field


class ExtractedParams(BaseModel):
    """Извлечённые параметры из запроса."""
    standard: Optional[str] = None
    thread: Optional[str] = None
    armature: Optional[str] = None
    angle: Optional[int] = None
    dy: Optional[int] = None
    
    def to_dict(self) -> dict:
        return {
            "standard": self.standard,
            "thread": self.thread,
            "armature": self.armature,
            "angle": self.angle,
            "dy": self.dy,
        }


class SearchResult(BaseModel):
    article: str
    name: str
    description: Optional[str] = None
    confidence: float
    standard: Optional[str] = None
    thread: Optional[str] = None
    armature: Optional[str] = None
    angle: Optional[int] = None
    dy: Optional[int] = None
    price: Optional[float] = None


class LLMChoice(BaseModel):
    article: str
    reason: str
    suitability: int = Field(..., ge=1, le=10)
    missing_params: List[str] = []


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)
    use_llm_analysis: bool = Field(True)


class SearchResponse(BaseModel):
    results: List[SearchResult]
    llm_choice: Optional[LLMChoice] = None
    query: str
    total_found: int
    processing_time_ms: float