"""Embedding service with caching."""

from typing import List
from sentence_transformers import SentenceTransformer
from backend.app.config import get_settings
from backend.app.logging_config import get_logger
import warnings

warnings.filterwarnings("ignore", message="You are sending unauthenticated requests")

logger = get_logger("embeddings")


class EmbeddingService:
    """Singleton embedding service."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        settings = get_settings()

        logger.info(
            "loading_embedding_model",
            model=settings.embedding_model,
            device=settings.embedding_device,
        )

        self.model = SentenceTransformer(
            settings.embedding_model,
            device=settings.embedding_device,
        )
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.batch_size = settings.embedding_batch_size

        self._initialized = True
        logger.info("embedding_model_loaded", dimension=self.dimension)

    def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts to embeddings."""
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    def encode_single(self, text: str) -> List[float]:
        """Encode single text."""
        return self.encode([text])[0]