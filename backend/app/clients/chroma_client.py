"""Thread-safe ChromaDB manager."""

import asyncio
from typing import Any, Optional

import chromadb
from chromadb.api.types import Include
from chromadb.config import Settings as ChromaSettings

from backend.app.config import get_settings
from backend.app.logging_config import get_logger

logger = get_logger("chroma")


class ChromaManager:
    """Singleton ChromaDB manager with async lock for writes."""

    _instance: Optional["ChromaManager"] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _init_lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        settings = get_settings()

        self.persist_dir = settings.chroma_persist_dir
        self.collection_name = settings.chroma_collection

        # ChromaDB client (thread-safe for reads)
        self._client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(
                anonymized_telemetry=False,
            ),
        )

        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        self._initialized = True
        logger.info(
            "chroma_initialized",
            collection=self.collection_name,
            count=self._collection.count(),
        )

    @property
    def collection(self):
        """Get ChromaDB collection."""
        return self._collection

    def count(self) -> int:
        """Get document count."""
        return self._collection.count()

    async def query(
            self,
            query_embeddings: list[list[float]],
            n_results: int = 10,
            where: Optional[dict] = None,
            include: Include = ["metadatas", "distances", "documents"],
    ) -> dict[str, Any]:
        """Query collection (read-only, thread-safe)."""
        # Run synchronous ChromaDB query in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                include=include,
            ),
        )

    async def add(
            self,
            documents: list[str],
            embeddings: list[list[float]],
            metadatas: list[dict],
            ids: list[str],
    ) -> None:
        """Add documents with write lock."""
        async with self._lock:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids,
                ),
            )
            logger.info("chroma_documents_added", count=len(documents))

    async def delete(self, ids: list[str]) -> None:
        """Delete documents with write lock."""
        async with self._lock:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._collection.delete(ids=ids),
            )
            logger.info("chroma_documents_deleted", count=len(ids))

    def reset(self) -> None:
        """Reset collection (admin only)."""
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.warning("chroma_collection_reset")