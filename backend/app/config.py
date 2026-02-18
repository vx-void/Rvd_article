# app/config.py
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    base_dir: Path = Path(__file__).resolve().parent.parent.parent

    data_dir: Path = base_dir / "backend" /"data"
    articles_file: Path = data_dir / "raw" / "articles.json"
    chroma_persist_dir: Path = data_dir / "chroma"
    chroma_path: Path = data_dir / "chroma"
    chroma_collection: str = "hydro_catalog"
    chroma_anonymized_telemetry: bool = False

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    embedding_batch_size: int = 32

    # Из .env (без значений по умолчанию — обязательно из файла)
    openrouter_api_key: str
    openrouter_model: str


@lru_cache
def get_settings():
    return Settings()