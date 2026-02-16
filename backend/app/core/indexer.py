"""Index management utilities."""

import json
from pathlib import Path
from typing import List

from backend.app.clients.chroma_client import ChromaManager
from backend.app.config import get_settings
from backend.app import EmbeddingService
from backend.app.logging_config import get_logger
from backend.app.models.article import Article

logger = get_logger("indexer")


class IndexManager:
    """Manage vector index operations."""

    def __init__(self):
        self.settings = get_settings()
        self.chroma = ChromaManager()
        self.embeddings = EmbeddingService()

    async def index_articles(self, articles: List[Article], clear_existing: bool = False) -> int:
        """Index articles to ChromaDB."""

        if clear_existing:
            logger.warning("clearing_existing_index")
            self.chroma.reset()

        if not articles:
            logger.warning("no_articles_to_index")
            return 0

        # Prepare data
        documents = []
        metadatas = []
        ids = []

        for i, art in enumerate(articles):
            documents.append(art.to_embedding_text())
            # Clean metadata for ChromaDB
            meta = {
                k: v for k, v in art.model_dump().items()
                if v is not None and k != 'price'  # Chroma has issues with floats sometimes
            }
            if art.price is not None:
                meta['price'] = float(art.price)
            metadatas.append(meta)
            ids.append(f"art_{art.article}_{i}")

        # Generate embeddings
        logger.info("generating_embeddings", count=len(documents))
        embeddings = self.embeddings.encode(documents)

        # Add to ChromaDB
        await self.chroma.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info("indexing_complete", count=len(articles))
        return len(articles)

    async def index_from_json(self, filepath: Path, clear_existing: bool = False) -> int:
        """Index from JSON file."""
        logger.info("loading_articles", path=filepath)

        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)

        articles = [Article(**item) for item in data]
        return await self.index_articles(articles, clear_existing)

    async def verify_index(self) -> dict:
        """Verify index integrity."""
        count = self.chroma.count()

        # Test query
        test_embedding = self.embeddings.encode_single("test fitting BSP")
        results = await self.chroma.query(
            query_embeddings=[test_embedding],
            n_results=1,
        )

        return {
            "document_count": count,
            "test_query_ok": len(results.get('ids', [[]])[0]) > 0,
        }