"""Конфигурация."""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки."""
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    data_dir: Path = Path("data")
    articles_file: Path = Path("data/raw/articles.json")
    chroma_persist_dir: Path = Path("data/chroma")
    chroma_path: Path = Path("data/chroma")  # для совместимости
    chroma_collection: str = "hydro_catalog"
    chroma_anonymized_telemetry: bool = False

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"  # или "cuda" если есть GPU
    embedding_batch_size: int = 32


#    class Config:
#        env_file = ".env"
#        case_sensitive = False


@lru_cache
def get_settings():
    return Settings()