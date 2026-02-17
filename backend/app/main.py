
import os

# Fix for Python 3.14 + ChromaDB compatibility
os.environ["CHROMA_SERVER_NOFILE"] = "65535"
os.environ["CHROMA_SERVER_WORKERS"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.router import api_router

app = FastAPI(
    title="Hydro Search API",
    version="2.0.0",
    description="API для поиска гидравлических компонентов",
)

# Разрешаем все CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"name": "Hydro Search API", "version": "2.0.0", "docs": "/docs"}