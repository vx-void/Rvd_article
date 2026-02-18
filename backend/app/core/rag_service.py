"""RAG сервис для поиска."""

import json
import time
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from backend.app.models.search import SearchResult
from backend.app.models.extraction import ExtractedParams, ExtractionConfidence
from backend.app.config import get_settings


class RAGService:
    """Поиск с векторной базой."""

    def __init__(self):
        settings = get_settings()

        # Эмбеддер
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        # ChromaDB
        self.chroma = chromadb.PersistentClient(path=str(settings.chroma_persist_dir))
        self.collection = self.chroma.get_or_create_collection("hydro_catalog")

        # Индексация при первом запуске
        if self.collection.count() == 0:
            self._build_index()

    def _build_index(self):
        """Построение индекса."""
        settings = get_settings()

        with open(settings.articles_file, encoding="utf-8") as f:
            articles = json.load(f)

        documents = []
        metadatas = []
        ids = []

        for i, art in enumerate(articles):
            # Текст для эмбеддинга
            doc = f"{art['name']}. {art.get('description', '')}"
            if art.get("standard"):
                doc += f". Стандарт {art['standard']}"
            if art.get("thread"):
                doc += f". Резьба {art['thread']}"

            documents.append(doc)
            metadatas.append({k: v for k, v in art.items() if v is not None})
            ids.append(str(i))

        # Генерация эмбеддингов
        embeddings = self.embedder.encode(documents).tolist()

        # Сохранение в ChromaDB
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

    def search(self, query: str, top_k: int = 5):
        """Поиск компонентов."""
        start = time.time()

        # Векторный поиск
        query_embedding = self.embedder.encode([query]).tolist()[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,  # Берем больше для реранжирования
            include=["metadatas", "distances"],
        )

        # Формирование результатов
        search_results = []
        for meta, distance in zip(results["metadatas"][0], results["distances"][0]):
            similarity = 1.0 - min(distance, 1.0)

            # Простое реранжирование по ключевым словам
            bonus = 0.0
            query_lower = query.lower()

            if meta.get("standard") and meta["standard"].lower() in query_lower:
                bonus += 0.2

            if meta.get("thread") and meta["thread"].lower() in query_lower:
                bonus += 0.15

            final_score = min(similarity + bonus, 1.0)

            search_results.append(
                SearchResult(
                    article=meta["article"],
                    name=meta["name"],
                    description=meta.get("description"),
                    confidence=final_score,
                    base_similarity=similarity,
                    parameter_matches=[],
                    extracted_params={},
                    standard=meta.get("standard"),
                    thread=meta.get("thread"),
                    armature=meta.get("armature"),
                    angle=meta.get("angle"),
                    dy=meta.get("dy"),

                )
            )

        # Сортировка и ограничение
        search_results.sort(key=lambda x: x.confidence, reverse=True)
        search_results = search_results[:top_k]

        # Извлечение параметров из запроса (простое)
        extracted = self._extract_params(query)

        # Добавляем extracted_params к результатам
        for r in search_results:
            r.extracted_params = extracted

        processing_time = (time.time() - start) * 1000

        return search_results, processing_time

    def _extract_params(self, query: str):
        """Простое извлечение параметров без LLM."""
        query_lower = query.lower()

        # Стандарт
        standard = None
        for std in ["BSP", "DKOL", "DKOS", "JIC", "JIS", "BSPT", "NPT", "ORFS"]:
            if std.lower() in query_lower:
                standard = std
                break

        # Тип
        armature = None
        if any(w in query_lower for w in ["папа", "штуцер", "наружн"]):
            armature = "male"
        elif any(w in query_lower for w in ["мама", "гайка", "внутренн"]):
            armature = "female"

        # Угол
        angle = None
        if "90" in query or "угол" in query_lower:
            angle = 90
        elif "45" in query:
            angle = 45
        elif "прямой" in query_lower or "0" in query:
            angle = 0

        # Резьба
        thread = None
        import re
        # Ищем размеры типа 1/2, 3/4, M18, M22
        match = re.search(r'(\d\/\d|M\d+)', query)
        if match:
            thread = match.group(1)

        return ExtractedParams(
            standard=standard,
            thread=thread,
            armature=armature,
            angle=angle,
            dy=None,
            component_type=None,
            confidence="medium",
        )

    def get_stats(self):
        """Статистика."""
        return {
            "total_articles": self.collection.count(),
            "embedding_model": "all-MiniLM-L6-v2",
        }