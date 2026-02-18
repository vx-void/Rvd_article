
import os

# Fix for Python 3.14 + ChromaDB compatibility
os.environ["CHROMA_SERVER_NOFILE"] = "65535"
os.environ["CHROMA_SERVER_WORKERS"] = "1"
os.environ["CHROME_PYDANTIC_V1"] = "0"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import api_router

app = FastAPI(
    title="Hydro Search API",
    version="1.2.0",
    description="API для поиска гидравлических компонентов",
)

# Разрешаем все CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Подключаем роутеры
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"name": "Hydro Search API", "version": "1.2.0"}