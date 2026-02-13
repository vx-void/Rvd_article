"""
Pydantic модели для RAG-сервиса.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Article(BaseModel):
    """
    Модель артикула из каталога.
    Соответствует структуре articles.json
    """
    article: str = Field(..., description="Артикул (SKU)")
    name: str = Field(..., description="Наименование")
    description: Optional[str] = Field(None, description="Описание")

    # Технические параметры
    standard: Optional[str] = Field(None, description="Стандарт: BSP, DKOL, JIC...")
    thread: Optional[str] = Field(None, description="Размер резьбы: 1/2, M18x1.5...")
    armature: Optional[str] = Field(None, description="Тип: male/female")
    angle: Optional[int] = Field(None, description="Угол: 0, 45, 90")
    dy: Optional[int] = Field(None, description="Условный проход Dy, мм")

    # Дополнительно
    price: Optional[float] = Field(None, description="Цена")
    series: Optional[str] = Field(None, description="Серия: лёгкая/тяжёлая")


class ExtractedParams(BaseModel):
    """
    Параметры, извлечённые LLM из запроса пользователя.
    Все поля optional — не домысливаем!
    """
    standard: Optional[str] = Field(None, description="Определённый стандарт")
    thread: Optional[str] = Field(None, description="Размер резьбы")
    armature: Optional[str] = Field(None, description="male/female")
    angle: Optional[int] = Field(None, description="Угол в градусах")
    dy: Optional[int] = Field(None, description="Условный проход")
    component_type: Optional[str] = Field(None, description="fitting/adapter/plug...")
    confidence: str = Field("medium", description="Уверенность LLM: high/medium/low")


class SearchRequest(BaseModel):
    """Входящий запрос на поиск."""
    query: str = Field(..., min_length=1, max_length=1000, description="Текст запроса")
    top_k: int = Field(5, ge=1, le=20, description="Количество результатов")


class SearchResult(BaseModel):
    """
    Результат поиска — один найденный артикул.
    """
    article: str = Field(..., description="Артикул")
    name: str = Field(..., description="Наименование")
    description: Optional[str] = Field(None, description="Описание")

    # Метрики качества
    confidence: float = Field(..., ge=0, le=1, description="Итоговая уверенность 0-1")
    base_similarity: float = Field(..., ge=0, le=1, description="Семантическая близость")
    parameter_matches: List[str] = Field(default_factory=list, description="Совпавшие параметры")

    # Для отладки и прозрачности
    extracted_params: Dict[str, Any] = Field(default_factory=dict, description="Что извлек LLM")


class SearchResponse(BaseModel):
    """Ответ API на поисковый запрос."""
    results: List[SearchResult]
    query: str
    total_found: int
    processing_time_ms: Optional[float] = None


class HealthResponse(BaseModel):
    """Ответ на проверку здоровья."""
    status: str
    version: str = "1.0.0"
    stats: Dict[str, Any]