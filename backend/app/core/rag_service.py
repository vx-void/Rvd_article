"""Production-ready RAG service."""

import time
from typing import List, Optional, Tuple

from backend.app.clients.chroma_client import ChromaManager
from backend.app.clients import OpenRouterClient
from backend.app.config import get_settings
from backend.app.core.cache import SearchCache
from backend.app import EmbeddingService
from backend.app.exceptions import LLMError
from backend.app.logging_config import get_logger
from backend.app.models.article import Article
from backend.app.models.extraction import ExtractedParams, ExtractionConfidence
from backend.app.models.search import SearchMetrics, SearchRequest, SearchResponse, SearchResult

logger = get_logger("rag_service")


class RAGService:
    """Retrieval-Augmented Generation service."""

    # Validation constants
    VALID_STANDARDS = {
        'BSP', 'BSPT', 'DKOL', 'DKOS', 'JIC', 'NPT', 'NPTF',
        'ORFS', 'DK', 'DKM', 'SFL', 'SFS', 'METRIC', 'BSP-DKOL',
        'BSP-DKOS', 'JIC-BSP', 'METRIC-BSP'
    }
    VALID_ARMATURES = {'male', 'female'}
    VALID_ANGLES = [0, 45, 90]

    def __init__(self):
        self.settings = get_settings()
        self.embeddings = EmbeddingService()
        self.chroma = ChromaManager()
        self.cache = SearchCache()

        # Prompts loaded lazily
        self._system_prompt: Optional[str] = None
        self._extraction_template: Optional[str] = None

        logger.info("rag_service_initialized")

    def _load_prompts(self) -> Tuple[str, str]:
        """Load system prompts from files."""
        if self._system_prompt is None:
            system_path = self.settings.prompts_dir / "system.txt"
            if system_path.exists():
                self._system_prompt = system_path.read_text(encoding='utf-8')
            else:
                self._system_prompt = "You are a hydraulic components expert."

        if self._extraction_template is None:
            extraction_path = self.settings.prompts_dir / "extraction.txt"
            if extraction_path.exists():
                self._extraction_template = extraction_path.read_text(encoding='utf-8')
            else:
                self._extraction_template = self._default_extraction_template()

        return self._system_prompt, self._extraction_template

    def _default_extraction_template(self) -> str:
        """Default template if file not found."""
        return """Extract parameters from query: \"{user_query}\"
Return JSON: {{"standard": "...", "thread": "...", "armature": "...", "angle": null, "dy": null, "component_type": "...", "confidence": "medium"}}"""

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Main search method."""
        start_time = time.time()

        # Check cache
        cached = self.cache.get(request.query, request.top_k, request.filters)
        if cached:
            logger.debug("cache_hit", query=request.query[:50])
            return cached

        metrics = SearchMetrics()

        # Step 1: Extract parameters via LLM
        extraction_start = time.time()
        extracted = await self._extract_parameters(request.query)
        metrics.extraction_time_ms = (time.time() - extraction_start) * 1000

        # Step 2: Retrieve candidates
        retrieval_start = time.time()
        candidates = await self._retrieve_candidates(request.query, request.filters)
        metrics.retrieval_time_ms = (time.time() - retrieval_start) * 1000

        # Step 3: Rerank
        rerank_start = time.time()
        results = self._rerank_candidates(
            candidates,
            extracted,
            request.top_k,
            request.min_confidence or self.settings.min_confidence_threshold,
        )
        metrics.rerank_time_ms = (time.time() - rerank_start) * 1000

        # Calculate metrics
        metrics.total_results = len(results)
        metrics.processing_time_ms = (time.time() - start_time) * 1000

        response = SearchResponse(
            results=results,
            query=request.query,
            total_found=len(results),
            metrics=metrics,
            extracted_params=extracted.to_dict() if extracted.has_parameters() else None,
        )

        # Cache result
        self.cache.set(request.query, request.top_k, request.filters, response)

        logger.info(
            "search_completed",
            query=request.query[:50],
            results=len(results),
            time_ms=metrics.processing_time_ms,
        )

        return response

    async def _extract_parameters(self, query: str) -> ExtractedParams:
        """Extract parameters using LLM."""
        system_prompt, template = self._load_prompts()
        user_prompt = template.format(
            system_prompt=system_prompt,
            user_query=query,
        )

        try:
            async with OpenRouterClient() as llm:
                raw = await llm.extract_json(
                    system_prompt="You are a hydraulic engineer. Return only JSON, no explanations.",
                    user_prompt=user_prompt,
                )

            return self._validate_extracted(raw, query)

        except LLMError as e:
            logger.error("extraction_failed", error=str(e), query=query[:50])
            # Return empty extraction on failure
            return ExtractedParams(raw_query=query, confidence=ExtractionConfidence.LOW)

    def _validate_extracted(self, raw: dict, query: str) -> ExtractedParams:
        """Validate and clean extracted parameters."""

        # Standard
        standard = raw.get('standard')
        if standard:
            standard = str(standard).upper()
            if standard not in self.VALID_STANDARDS:
                # Fuzzy match
                for valid in self.VALID_STANDARDS:
                    if valid in standard or standard in valid:
                        standard = valid
                        break
                else:
                    standard = None

        # Armature
        armature = raw.get('armature')
        if armature:
            arm_lower = str(armature).lower()
            if any(x in arm_lower for x in ['пап', 'штуц', 'наруж', 'male']):
                armature = 'male'
            elif any(x in arm_lower for x in ['мам', 'гайк', 'внутр', 'female']):
                armature = 'female'
            else:
                armature = None

        # Angle
        angle = raw.get('angle')
        if angle is not None:
            try:
                angle = int(angle)
                if angle not in self.VALID_ANGLES:
                    angle = min(self.VALID_ANGLES, key=lambda x: abs(x - angle))
            except (ValueError, TypeError):
                angle = None

        # Dy
        dy = raw.get('dy')
        if dy is not None:
            try:
                dy = int(dy)
                if not (4 <= dy <= 100):
                    dy = None
            except (ValueError, TypeError):
                dy = None

        # Thread
        thread = raw.get('thread')
        if thread and not isinstance(thread, str):
            thread = None

        # Component type
        comp_type = raw.get('component_type')
        if comp_type:
            type_lower = str(comp_type).lower()
            if any(x in type_lower for x in ['фитинг', 'fitting']):
                comp_type = 'fitting'
            elif any(x in type_lower for x in ['переход', 'адаптер', 'adapter']):
                comp_type = 'adapter'
            elif any(x in type_lower for x in ['заглушк', 'пробк', 'plug']):
                comp_type = 'plug'
            else:
                comp_type = None

        # Confidence
        conf = raw.get('confidence', 'medium')
        try:
            confidence = ExtractionConfidence(conf.lower())
        except ValueError:
            confidence = ExtractionConfidence.MEDIUM

        return ExtractedParams(
            standard=standard,
            thread=thread,
            armature=armature,
            angle=angle,
            dy=dy,
            component_type=comp_type,
            confidence=confidence,
            raw_query=query,
        )

    async def _retrieve_candidates(
        self,
        query: str,
        filters: Optional[dict],
    ) -> List[dict]:
        """Retrieve candidates from vector store."""
        query_embedding = self.embeddings.encode_single(query)

        # Build where clause from filters
        where_clause = None
        if filters:
            where_clause = {}
            for key, value in filters.items():
                if value is not None:
                    where_clause[key] = value

        results = await self.chroma.query(
            query_embeddings=[query_embedding],
            n_results=self.settings.top_k_retrieve,
            where=where_clause,
            include=["metadatas", "distances", "documents"],
        )

        candidates = []
        for meta, distance, doc in zip(
            results['metadatas'][0],
            results['distances'][0],
            results['documents'][0],
        ):
            # Convert cosine distance to similarity
            similarity = 1.0 - min(distance, 1.0)
            candidates.append({
                'article': Article(**meta),
                'similarity': max(0.0, similarity),
                'matched_text': doc,
            })

        return candidates

    def _rerank_candidates(
        self,
        candidates: List[dict],
        extracted: ExtractedParams,
        top_k: int,
        min_confidence: float,
    ) -> List[SearchResult]:
        """Rerank candidates using extracted parameters."""

        scored = []

        for cand in candidates:
            art = cand['article']
            base_score = cand['similarity']
            bonus = 0.0
            matches = []

            # Standard match (+0.30)
            if extracted.standard and art.standard:
                if extracted.standard.upper() == art.standard.upper():
                    bonus += 0.30
                    matches.append(f"стандарт:{art.standard}")
                elif extracted.standard in str(art.standard).upper():
                    bonus += 0.15

            # Thread match (+0.25)
            if extracted.thread and art.thread:
                if self._threads_match(extracted.thread, art.thread):
                    bonus += 0.25
                    matches.append(f"резьба:{art.thread}")

            # Armature match (+0.20)
            if extracted.armature and art.armature:
                if extracted.armature.lower() in str(art.armature).lower():
                    bonus += 0.20
                    matches.append(f"тип:{art.armature}")

            # Angle match (+0.15)
            if extracted.angle is not None and art.angle is not None:
                if extracted.angle == art.angle:
                    bonus += 0.15
                    matches.append(f"угол:{art.angle}°")

            # Dy match (+0.10)
            if extracted.dy is not None and art.dy is not None:
                if extracted.dy == art.dy:
                    bonus += 0.10
                    matches.append(f"Dy:{art.dy}")

            # Penalty for type mismatch
            if extracted.component_type and art.component_type:
                if extracted.component_type != art.component_type:
                    bonus -= 0.05

            final_score = min(base_score + bonus, 1.0)

            if final_score >= min_confidence:
                scored.append({
                    'article': art,
                    'score': final_score,
                    'base_similarity': base_score,
                    'matches': matches,
                })

        # Sort by score
        scored.sort(key=lambda x: x['score'], reverse=True)

        # Build results
        results = []
        for s in scored[:top_k]:
            art = s['article']
            results.append(SearchResult(
                article=art.article,
                name=art.name,
                description=art.description,
                confidence=s['score'],
                base_similarity=s['base_similarity'],
                parameter_matches=s['matches'],
                extracted_params=extracted.to_dict(),
                standard=art.standard,
                thread=art.thread,
                armature=art.armature,
                angle=art.angle,
                dy=art.dy,
                price=art.price,
            ))

        return results

    def _threads_match(self, query_thread: str, article_thread: str) -> bool:
        """Fuzzy thread matching."""
        q = str(query_thread).lower().replace('×', 'x').replace('*', 'x').replace(' ', '')
        a = str(article_thread).lower().replace('×', 'x').replace('*', 'x').replace(' ', '')

        if q == a:
            return True

        # Normalize metric threads
        if 'm' in q and 'm' in a:
            q_norm = q.replace('м', 'm').replace('х', 'x')
            a_norm = a.replace('м', 'm').replace('х', 'x')
            if q_norm == a_norm:
                return True

        return False

    def get_stats(self) -> dict:
        """Get service statistics."""
        return {
            'total_articles': self.chroma.count(),
            'embedding_dimension': self.embeddings.dimension,
            'embedding_model': self.settings.embedding_model,
            'cache_stats': self.cache.stats(),
        }