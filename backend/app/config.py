import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import  load_dotenv

load_dotenv()
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


    app_name: str = "Hydro Search"
    app_version: str = "1.2.0"
    debug: bool = False
    environment: str = "production"

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Security
    api_key_header: str = "X-API-Key"
    api_keys: List[str] = Field(default_factory=list)
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # CORS
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    cors_allow_credentials: bool = True

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 30
    rate_limit_window: int = 60  # seconds
    redis_url: Optional[str] = None  # fallback to memory

    # OpenRouter (LLM)
    openrouter_api_key: str
    openrouter_model: str = os.getenv('GEMMA_3_27B_IT')
    openrouter_timeout: int = 30
    openrouter_max_retries: int = 3
    openrouter_temperature: float = 0.05

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    embedding_batch_size: int = 32

    # ChromaDB
    chroma_persist_dir: Path = Path("data/chroma")
    chroma_collection: str = "hydro_catalog"
    chroma_anonymized_telemetry: bool = False

    # Search
    top_k_retrieve: int = 20
    top_k_return: int = 5
    min_confidence_threshold: float = 0.3

    # Data
    data_dir: Path = Path("data")
    articles_file: Path = Path("data/raw/articles.json")
    prompts_dir: Path = Path("data/prompts")

    # Monitoring
    enable_metrics: bool = True
    log_level: str = "INFO"
    log_format: str = "json"

    @field_validator("api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [k.strip() for k in v.split(",") if k.strip()]
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def chroma_path(self) -> str:
        return str(self.chroma_persist_dir.absolute())


@lru_cache
def get_settings() -> Settings:
    return Settings()