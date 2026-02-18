"""RAG сервис с двухэтапным поиском: векторный + LLM-анализ."""

import time
import json
import re
from typing import Tuple, Optional

from backend.app.clients.chroma_client import ChromaManager
from backend.app.clients.openrouter_client import OpenRouterClient
from backend.app.core.embeddings import EmbeddingService
from backend.app.core.prompt_loader import load_prompt
from backend.app.models.search import SearchResult, LLMChoice, ExtractedParams
from backend.app.logging_config import get_logger

logger = get_logger("rag_service")


class RAGService:
    """Двухэтапный поиск: векторный → реранжирование → LLM-анализ."""

    def __init__(self):
        self.embeddings = EmbeddingService()
        self.chroma = ChromaManager()
        self.llm = OpenRouterClient()

    async def search(
        self,
        query: str,
        top_k: int = 5,
        use_llm_analysis: bool = True,
    ) -> Tuple[list[SearchResult], Optional[LLMChoice], float]:
        """
        Двухэтапный поиск.

        Returns:
            - список результатов (top_k)
            - выбор LLM (если use_llm_analysis=True)
            - время обработки в мс
        """
        start = time.time()

        # Этап 1: Извлечение параметров
        extracted = self._extract_params(query)
        logger.info("params_extracted", params=extracted.to_dict())

        # Этап 2: Векторный поиск (берём много для реранжирования)
        query_embedding = self.embeddings.encode_single(query)

        chroma_results = await self.chroma.query(
            query_embeddings=[query_embedding],
            n_results=20,
            include=["metadatas", "distances"],
        )

        # Этап 3: Реранжирование
        candidates = self._rerank(chroma_results, extracted, top_n=10)

        # Этап 4: LLM-анализ топ-3 (опционально)
        llm_choice = None
        if use_llm_analysis and len(candidates) >= 3:
            llm_choice = await self._llm_select_best(query, candidates[:3])
            logger.info("llm_selected",
                       article=llm_choice.article,
                       suitability=llm_choice.suitability)

        processing_time = (time.time() - start) * 1000
        return candidates[:top_k], llm_choice, processing_time

    def _extract_params(self, query: str) -> ExtractedParams:
        """Упрощённое rule-based извлечение."""
        q = query.lower()

        # Стандарт
        standards = ["BSP", "DKOL", "DKOS", "JIC", "JIS", "BSPT", "NPT", "ORFS"]
        standard = next((s for s in standards if s.lower() in q), None)

        # Тип (фитинг = male по умолчанию)
        armature = None
        if any(w in q for w in ["фитинг", "штуцер", "папа", "наружн", "male"]):
            armature = "male"
        elif any(w in q for w in ["гайка", "мама", "внутренн", "female"]):
            armature = "female"

        # Резьба
        thread_match = re.search(r'(\d\/\d+"?|M\d+[\d\.]*)', query)
        thread = thread_match.group(1) if thread_match else None

        # Угол из скобок или чисел
        angle_match = re.search(r'\((0|45|90)\)', query)
        angle = int(angle_match.group(1)) if angle_match else \
                (90 if "90" in query else
                 45 if "45" in query else
                 0 if any(w in q for w in ["прямой", "(0)"]) else None)

        # Dy
        dy_match = re.search(r'\b(0[468]|1[02]|[2468])\b', query)
        dy = int(dy_match.group(1)) if dy_match else None

        return ExtractedParams(
            standard=standard,
            thread=thread,
            armature=armature,
            angle=angle,
            dy=dy,
        )

    def _rerank(
        self,
        chroma_results: dict,
        extracted: ExtractedParams,
        top_n: int = 10,
    ) -> list[SearchResult]:
        """Реранжирование с бонусами за совпадения."""
        results = []

        for meta, distance in zip(
            chroma_results["metadatas"][0],
            chroma_results["distances"][0]
        ):
            similarity = 1.0 - min(distance, 1.0)
            score = similarity

            # Бонусы за точные совпадения
            bonuses = {
                "standard": 0.25,
                "thread": 0.20,
                "armature": 0.20,
                "angle": 0.15,
                "dy": 0.15,
            }

            for field, bonus in bonuses.items():
                if getattr(extracted, field) is not None:
                    if meta.get(field) == getattr(extracted, field):
                        score += bonus

            results.append(SearchResult(
                article=meta["article"],
                name=meta["name"],
                description=meta.get("description"),
                confidence=round(min(score, 1.0), 3),
                standard=meta.get("standard"),
                thread=meta.get("thread"),
                armature=meta.get("armature"),
                angle=meta.get("angle"),
                dy=meta.get("dy"),
                price=meta.get("price"),
            ))

        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:top_n]

    async def _llm_select_best(
        self,
        query: str,
        candidates: list[SearchResult],
    ) -> LLMChoice:
        """LLM выбирает лучший товар из кандидатов."""

        # Формируем описание кандидатов
        lines = []
        for i, c in enumerate(candidates, 1):
            lines.append(
                f"Товар {i}:\n"
                f"  Артикул: {c.article}\n"
                f"  Название: {c.name}\n"
                f"  Параметры: стандарт={c.standard or '-'}, "
                f"резьба={c.thread or '-'}, тип={c.armature or '-'}, "
                f"угол={c.angle if c.angle is not None else '-'}°\n"
                f"  Уверенность поиска: {c.confidence:.0%}"
            )

        # Загружаем и форматируем промпт
        prompt = load_prompt(
            "llm_selection",
            query=query,
            candidates="\n\n".join(lines),
        )

        try:
            response = await self.llm.generate(
                system_prompt="Ты эксперт по гидравлике. Отвечай только JSON.",
                user_prompt=prompt,
                temperature=0.1,
                max_tokens=300,
            )

            data = self._extract_json(response)

            return LLMChoice(
                article=data.get("article", candidates[0].article),
                reason=data.get("reason", "Выбран по релевантности"),
                suitability=data.get("suitability", 5),
                missing_params=data.get("missing_params", []),
            )

        except Exception as e:
            logger.error("llm_selection_failed", error=str(e))
            return LLMChoice(
                article=candidates[0].article,
                reason=f"Выбран по релевантности (LLM ошибка: {str(e)[:50]})",
                suitability=5,
                missing_params=[],
            )

    def _extract_json(self, text: str) -> dict:
        """Извлечение JSON из ответа LLM."""
        # Ищем JSON объект
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        logger.warning("json_parse_failed", text=text[:200])
        return {}