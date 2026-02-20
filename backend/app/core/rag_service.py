"""RAG сервис с двухэтапным определением: тип → параметры → поиск."""

import time
import json
import re
from pathlib import Path
from typing import Tuple, Optional, ClassVar, Literal, List

from backend.app.clients.chroma_client import ChromaManager
from backend.app.clients.openrouter_client import OpenRouterClient
from backend.app.core.embeddings import EmbeddingService
from backend.app.models.extraction import ExtractedParams, ExtractionConfidence
from backend.app.models.search import SearchResult, LLMChoice
from backend.app.logging_config import get_logger

logger = get_logger("rag_service")

ComponentType = Literal["fitting", "adapter", "unknown"]


class RAGService:
    """Трёхэтапный поиск: определение типа → извлечение параметров → поиск."""

    _prompt_cache: ClassVar[dict[str, str]] = {}

    def __init__(self):
        self.embeddings = EmbeddingService()
        self.chroma = ChromaManager()
        self.llm = OpenRouterClient()

    @classmethod
    def _load_prompt(cls, name: str, **kwargs) -> str:
        """Загрузка и кэширование промптов из файлов."""
        if name not in cls._prompt_cache:
            path = Path(__file__).parent.parent.parent / "app" / "prompts" / f"{name}.txt"
            if not path.exists():
                raise FileNotFoundError(f"Промпт не найден: {path}")
            cls._prompt_cache[name] = path.read_text(encoding="utf-8")

        template = cls._prompt_cache[name]
        return template.format(**kwargs) if kwargs else template

    async def search(self, query: str, top_k: int = 5, use_llm_analysis: bool = True, ) -> (Tuple)[list[SearchResult], Optional[LLMChoice], float]:
        """Трёхэтапный поиск: тип → параметры → векторный → реранжирование → LLM."""
        start = time.time()

        # ЭТАП 1: Определение типа компонента
        #component_type = await self._determine_component_type(query)
        #logger.info("component_type_detected", type=component_type, query=query)

        # ЭТАП 2: Извлечение параметров с учётом типа
        extracted = self._extract_params(query)
        #component_type = extracted.component_type
        logger.info("params_extracted",
                   type=extracted.component_type,
                   params=extracted.to_dict())

        # ЭТАП 3: Векторный поиск
        query_embedding = self.embeddings.encode_single(query)

        try:
            chroma_results = await self.chroma.query(
                query_embeddings=[query_embedding],
                n_results=20,
                include=["metadatas", "distances"],
            )
        except Exception as e:
            logger.error("chroma_query_failed", error=str(e))
            return [], None, (time.time() - start) * 1000

        if not chroma_results.get("metadatas") or not chroma_results["metadatas"][0]:
            logger.warning("no_chroma_results", query=query)
            return [], None, (time.time() - start) * 1000

        # ЭТАП 4: Реранжирование с учётом типа
        candidates = self._rerank(chroma_results, extracted, component_type, top_n=10)

        # ЭТАП 5: LLM-анализ топ-3
        llm_choice = None
        if use_llm_analysis and len(candidates) >= 3:
            llm_choice = await self._llm_select_best(query, candidates[:3], component_type, extracted)
            logger.info("llm_selected",
                       article=llm_choice.article,
                       suitability=llm_choice.suitability)

        processing_time = (time.time() - start) * 1000
        return candidates[:top_k], llm_choice, processing_time

    async def _determine_component_type(self, query: str) -> ComponentType:
        """LLM определяет тип компонента: fitting или adapter."""
        try:
            # Используем существующий промпт detect_component
            prompt = self._load_prompt("detect_component", chat_input=query)

            response = await self.llm.generate(
                system_prompt=prompt,
                user_prompt=query,
                temperature=0.1,
                max_tokens=200,
            )

            data = self.llm._parse_json(response)

            # Парсим массив из detect_component
            if isinstance(data, list) and len(data) > 0:
                detected_type = data[0].get("type", "unknown")
            elif isinstance(data, dict):
                detected_type = data.get("type", "unknown")
            else:
                detected_type = "unknown"

            # Нормализация типа
            type_map = {
                "фитинг": "fitting",
                "fitting": "fitting",
                "адаптер": "adapter",
                "adapter": "adapter",
            }

            return type_map.get(detected_type.lower(), "unknown")

        except Exception as e:
            logger.error("type_classification_failed", error=str(e), query=query)
            return self._fallback_type_detection(query)

    def _fallback_type_detection(self, query: str) -> ComponentType:
        """Rule-based fallback при ошибке LLM."""
        q = query.lower()

        # Признаки адаптера
        adapter_markers = ["переходник", "переход", "→", "/", " с ", " на ", "из "]
        has_adapter_marker = any(m in q for m in adapter_markers)

        # Признаки фитинга
        if re.search(r'\b(дн|dn)\s*\d+', q):
            return "fitting"

        if has_adapter_marker:
            return "adapter"

        return "unknown"

    def _extract_params(self, query: str) -> ExtractedParams:
        """Извлечение параметров с автоопределением типа."""
        q = query.lower()

        # Сначала проверяем признаки адаптера
        adapter_markers = ["переходник", "переход", "→", "/", " с ", " на ", "из "]
        is_adapter = any(m in q for m in adapter_markers)

        # Или две резьбы без DN/угла
        threads = re.findall(r'\d{1,2}\s*[x×]\s*\d\.?\d*', query)
        is_adapter = is_adapter or len(threads) >= 2

        if is_adapter:
            return self._extract_adapter_params(query)

        # Иначе фитинг (включая fallback)
        return self._extract_fitting_params(query)

    def _extract_fitting_params(self, query: str) -> ExtractedParams:
        """Извлечение параметров для фитинга."""
        q = query.lower()

        # DN (dy)
        dn_match = re.search(r'(?:дн|dn)\s*(\d+)', q)
        if not dn_match:
            dn_match = re.search(r'\b(6|8|10|16|20|25|32|40|50)\b', q)
        dy = int(dn_match.group(1)) if dn_match else None

        # Стандарт
        standards = ["BSP", "DKOL", "DKOS", "DK", "JIC", "JIS", "BSPT", "NPT", "ORFS"]
        standard = next((s for s in standards if s.lower() in q), None)

        # Тип (armature)
        armature = None
        if any(w in q for w in ["гайка", "мама", "внутренн"]):
            armature = "female"
        elif any(w in q for w in ["штуцер", "папа", "наружн"]):
            armature = "male"

        # Резьба
        thread = self._extract_thread(query)

        # Угол
        angle = self._extract_angle(q)

        # Уверенность
        found_params = sum(x is not None for x in [standard, thread, armature, angle, dy])
        confidence_level = found_params / 5
        confidence = (
            ExtractionConfidence.HIGH if confidence_level >= 0.8
            else ExtractionConfidence.MEDIUM if confidence_level >= 0.5
            else ExtractionConfidence.LOW
        )

        return ExtractedParams(
            standard=standard,
            thread=thread,
            armature=armature,
            angle=angle,
            dy=dy,
            component_type="fitting",
            confidence=confidence,
            raw_query=query,
        )

    def _extract_adapter_params(self, query: str) -> ExtractedParams:
        """Извлечение параметров для адаптера."""
        q = query.lower()

        # Стандарты
        standards = ["BSP", "DKOL", "DKOS", "DK", "JIC", "JIS", "BSPT", "NPT", "ORFS"]
        found_standards = [s for s in standards if s.lower() in q]
        standard = found_standards[0] if found_standards else None

        # Исполнение (armature для адаптера — комбинированное)
        armature = None
        if any(p in q for p in ["ш-г", "штуцер-гайка", "папа-мама"]):
            armature = "male-female"
        elif any(p in q for p in ["г-г", "гайка-гайка", "мама-мама"]):
            armature = "female-female"
        elif any(p in q for p in ["ш-ш", "штуцер-штуцер", "папа-папа"]):
            armature = "male-male"

        # Резьбы (вход/выход)
        thread = self._extract_adapter_threads(query)

        # Уверенность
        found_params = sum(x is not None for x in [standard, thread, armature])
        confidence_level = found_params / 3
        confidence = (
            ExtractionConfidence.HIGH if confidence_level >= 0.8
            else ExtractionConfidence.MEDIUM if confidence_level >= 0.5
            else ExtractionConfidence.LOW
        )

        return ExtractedParams(
            standard=standard,
            thread=thread,
            armature=armature,
            angle=None,
            dy=None,
            component_type="adapter",
            confidence=confidence,
            raw_query=query,
        )

    def _extract_thread(self, query: str) -> Optional[str]:
        """Извлечение резьбы."""
        # Метрическая: 18×1.5, M22×1.5
        metric_match = re.search(r'(\d{1,2})\s*[x×]\s*(\d\.?\d*)', query)
        if metric_match:
            return f"{metric_match.group(1)}×{metric_match.group(2)}"

        m_match = re.search(r'[Mm](\d+)\s*[x×]?\s*(\d\.?\d*)?', query)
        if m_match:
            diameter = m_match.group(1)
            pitch = m_match.group(2) if m_match.group(2) else "1.5"
            return f"M{diameter}×{pitch}"

        # Дюймовая: 1/2", 3/4"
        inch_match = re.search(r'(\d\/\d+|\d+\s+\d\/\d+)"?', query)
        if inch_match:
            return inch_match.group(1) + '"'

        return None

    def _extract_angle(self, q: str) -> Optional[int]:
        """Извлечение угла."""
        angle_match = re.search(r'\((0|45|90)\)', q)
        if angle_match:
            return int(angle_match.group(1))

        if "90" in q or "девяносто" in q:
            return 90
        if "45" in q:
            return 45
        if any(w in q for w in ["прямой", "(0)"]):
            return 0

        return None

    def _extract_adapter_threads(self, query: str) -> Optional[str]:
        """Извлечение резьб для адаптера."""
        threads = []

        metric_matches = re.findall(r'(\d{1,2})\s*[x×]\s*(\d\.?\d*)', query)
        for m in metric_matches:
            threads.append(f"{m[0]}×{m[1]}")

        inch_matches = re.findall(r'(\d\/\d+|\d+\s+\d\/\d+)"?', query)
        for m in inch_matches:
            threads.append(m + '"')

        if len(threads) >= 2:
            return f"{threads[0]} → {threads[1]}"
        elif threads:
            return threads[0]

        return None

    def _rerank(
        self,
        chroma_results: dict,
        extracted: ExtractedParams,
        component_type: ComponentType,
        top_n: int = 10,
    ) -> list[SearchResult]:
        """Реранжирование с учётом типа."""
        results = []

        # Бонусы для фитинга
        fitting_bonuses = {
            "standard": 0.25, "thread": 0.20, "armature": 0.20,
            "angle": 0.15, "dy": 0.15,
        }

        # Бонусы для адаптера
        adapter_bonuses = {
            "standard": 0.35, "thread": 0.35, "armature": 0.25,
            "angle": 0.0, "dy": 0.0,
        }

        bonuses = fitting_bonuses if component_type == "fitting" else adapter_bonuses

        for meta, distance in zip(
            chroma_results["metadatas"][0],
            chroma_results["distances"][0]
        ):
            similarity = 1.0 - min(distance, 1.0)
            score = similarity

            # Штраф за несовпадение типа
            meta_type = meta.get("component_type", "fitting")
            if meta_type != component_type and component_type != "unknown":
                score -= 0.3

            for field, bonus in bonuses.items():
                extracted_val = getattr(extracted, field, None)
                if extracted_val is not None and meta.get(field) == extracted_val:
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
        component_type: ComponentType,
        extracted: ExtractedParams,
    ) -> LLMChoice:
        """LLM выбирает лучший товар."""

        lines = []
        for i, c in enumerate(candidates, 1):
            if component_type == "adapter":
                params = f"стандарт={c.standard or '-'}, резьбы={c.thread or '-'}, исполнение={c.armature or '-'}"
            else:
                params = f"DN={c.dy or '-'}, стандарт={c.standard or '-'}, резьба={c.thread or '-'}, тип={c.armature or '-'}, угол={c.angle if c.angle is not None else '-'}°"

            lines.append(
                f"Товар {i}:\n"
                f"  Артикул: {c.article}\n"
                f"  Название: {c.name}\n"
                f"  Параметры: {params}\n"
                f"  Уверенность: {c.confidence:.0%}"
            )

        # Выбираем промпт в зависимости от типа
        prompt_name = f"llm_selection_{component_type}"

        try:
            prompt = self._load_prompt(
                prompt_name,
                query=query,
                candidates="\n\n".join(lines),
            )
        except FileNotFoundError:
            # Fallback на универсальный промпт
            prompt = self._load_prompt("llm_selection", query=query, candidates="\n\n".join(lines))

        try:
            response = await self.llm.generate(
                system_prompt=f"Ты эксперт по гидравлике. Запрос на {component_type}. Отвечай только JSON.",
                user_prompt=prompt,
                temperature=0.1,
                max_tokens=400,
            )

            data = self.llm._parse_json(response)

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
                reason=f"Выбран по релевантности (ошибка: {str(e)[:50]})",
                suitability=5,
                missing_params=[],
            )


