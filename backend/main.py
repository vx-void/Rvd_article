"""
FastAPI приложение для RAG-поиска гидравлических компонентов.
Использует OpenRouter для LLM.
"""

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from models import SearchRequest, SearchResponse, SearchResult, HealthResponse
from rag_service import RAGService, RAGConfig


# Инициализация приложения
app = FastAPI(
    title="Hydro RAG Search API",
    description="Поиск гидравлических компонентов через RAG + OpenRouter",
    version="1.0.0"
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный сервис (singleton)
rag_service: Optional[RAGService] = None


@app.on_event("startup")
async def startup_event():
    """Инициализация при старте."""
    global rag_service

    # Конфигурация из переменных окружения
    config = RAGConfig(
        data_dir=Path(os.getenv("DATA_DIR", "data")),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-7b-instruct"),
        top_k_retrieve=int(os.getenv("TOP_K_RETRIEVE", "20")),
        top_k_return=int(os.getenv("TOP_K_RETURN", "5")),
    )

    rag_service = RAGService(config)
    print("✅ RAG сервис инициализирован")


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Поиск гидравлических компонентов.

    Примеры запросов:
    - "фитинг BSP 1/2 штуцер"
    - "уголок DKOL M18 папа"
    - "переходник с 1/2 BSP на M22 DKOS"
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="Сервис не инициализирован")

    try:
        results, processing_time = rag_service.search(request.query, request.top_k)

        return SearchResponse(
            results=results,
            query=request.query,
            total_found=len(results),
            processing_time_ms=round(processing_time, 2)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Проверка здоровья сервиса."""
    if not rag_service:
        return HealthResponse(
            status="initializing",
            stats={"error": "Сервис не готов"}
        )

    return HealthResponse(
        status="healthy",
        stats=rag_service.get_stats()
    )


@app.get("/api/models")
async def list_models():
    """Список доступных моделей OpenRouter (для справки)."""
    if not rag_service:
        raise HTTPException(status_code=503, detail="Сервис не инициализирован")

    try:
        models = rag_service.llm.list_available_models()
        return {
            "current_model": rag_service.config.openrouter_model,
            "recommended": rag_service.llm.RECOMMENDED_MODELS,
            "available_count": len(models),
            "sample_models": models[:5] if models else []
        }
    except Exception as e:
        return {
            "current_model": rag_service.config.openrouter_model,
            "recommended": rag_service.llm.RECOMMENDED_MODELS,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)