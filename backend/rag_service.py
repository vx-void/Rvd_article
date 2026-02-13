"""
RAG-сервис для поиска гидравлических компонентов.
Использует OpenRouter для LLM и локальный эмбеддер + ChromaDB.
"""

import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

import chromadb
from sentence_transformers import SentenceTransformer

from models import Article, SearchResult, ExtractedParams
from openrouter_client import OpenRouterClient


@dataclass
class RAGConfig:
    """Конфигурация сервиса."""
    data_dir: Path = Path("data")
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    openrouter_model: str = "qwen/qwen-2.5-7b-instruct"
    collection_name: str = "hydro_catalog"
    top_k_retrieve: int = 20
    top_k_return: int = 5


class RAGService:
    """
    Retrieval-Augmented Generation для гидравлических компонентов.
    """

    # Допустимые значения для валидации
    VALID_STANDARDS = {
        'BSP', 'BSPT', 'DKOL', 'DKOS', 'JIC', 'NPT', 'NPTF',
        'ORFS', 'DK', 'DKM', 'SFL', 'SFS', 'METRIC', 'BSP-DKOL',
        'BSP-DKOS', 'JIC-BSP', 'METRIC-BSP'
    }
    VALID_ARMATURES = {'male', 'female', 'unknown', 'male-male', 'male-female'}
    VALID_TYPES = {'fitting', 'adapter', 'plug', 'coupling', 'banjo', 'unknown'}
    VALID_ANGLES = [0, 45, 90]

    def __init__(self, config: RAGConfig = None):
        self.config = config or RAGConfig()
        self.data_dir = self.config.data_dir

        # 1. Локальный эмбеддер
        self._init_embedder()

        # 2. Локальная векторная БД
        self._init_vector_store()

        # 3. OpenRouter клиент
        self._init_llm_client()

        # Загружаем промпты
        self._load_prompts()

        # Индексация при первом запуске
        if self.collection.count() == 0:
            self._build_index()

        print(f"RAG сервис готов. В индексе: {self.collection.count()} артикулов")

    def _init_embedder(self):
        """Инициализация локального эмбеддера."""
        print(f"Загрузка эмбеддера: {self.config.embedding_model}")
        self.embedder = SentenceTransformer(self.config.embedding_model)
        self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
        print(f"Размерность эмбеддингов: {self.embedding_dim}")

    def _init_vector_store(self):
        """Инициализация ChromaDB."""
        chroma_path = self.data_dir / "chroma"
        self.chroma = chromadb.PersistentClient(path=str(chroma_path))
        self.collection = self.chroma.get_or_create_collection(
            name=self.config.collection_name
        )

    def _init_llm_client(self):
        """Инициализация OpenRouter клиента."""
        self.llm = OpenRouterClient(
            model=self.config.openrouter_model,
            temperature=0.05,
            max_tokens=512
        )

    def _load_prompts(self):
        """Загрузка системных промптов."""
        prompts_dir = self.data_dir / "prompts"

        system_path = prompts_dir / "system.txt"
        self.system_prompt = system_path.read_text(encoding='utf-8') if system_path.exists() else ""

        extraction_path = prompts_dir / "extraction_template.txt"
        self.extraction_template = extraction_path.read_text(encoding='utf-8') if extraction_path.exists() else ""

    def _clean_metadata(self, art: dict) -> dict:
        """
        Очистка метаданных для ChromaDB.
        ChromaDB не поддерживает None и нестандартные типы!
        """
        cleaned = {}

        # Строковые поля
        for key in ['article', 'name', 'description', 'standard', 'thread',
                    'armature', 'series', 'component_type']:
            value = art.get(key)
            if value is not None:
                cleaned[key] = str(value)
            # None пропускаем — ChromaDB сама установит null

        # Числовые поля — только если не None
        for key in ['angle', 'dy']:
            value = art.get(key)
            if value is not None:
                try:
                    cleaned[key] = int(value)
                except (ValueError, TypeError):
                    pass  # Пропускаем невалидные числа

        # Float поля
        price = art.get('price')
        if price is not None:
            try:
                cleaned['price'] = float(price)
            except (ValueError, TypeError):
                pass

        return cleaned

    def _build_index(self):
        """Построение векторного индекса."""
        print("Построение индекса...")

        articles_path = self.data_dir / "articles.json"
        with open(articles_path, encoding='utf-8') as f:
            articles = json.load(f)

        documents = []
        metadatas = []
        ids = []

        for i, art in enumerate(articles):
            doc_text = self._enrich_for_embedding(art)
            documents.append(doc_text)

            # ОЧИЩАЕМ метаданные для ChromaDB!
            clean_meta = self._clean_metadata(art)
            metadatas.append(clean_meta)
            ids.append(str(i))

        # Батчевое кодирование
        print(f"Кодирование {len(documents)} документов...")
        embeddings = self.embedder.encode(
            documents,
            show_progress_bar=True,
            convert_to_numpy=True
        ).tolist()

        # Сохранение в ChromaDB
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Индекс построен: {len(documents)} артикулов")

    def _enrich_for_embedding(self, art: dict) -> str:
        """Обогащение текста для семантического поиска."""
        parts = [art.get('name', ''), art.get('description', '')]

        standard = art.get('standard')
        if standard:
            parts.append(f"Стандарт {standard}")
            synonyms = {
                'BSP': 'British Standard Pipe цилиндрическая дюймовая папа штуцер',
                'DKOL': 'DIN 2353 метрическая лёгкая серия 24 градуса конус',
                'DKOS': 'DIN 2353 метрическая тяжёлая серия высокое давление',
                'JIC': 'Joint Industry Council 74 градуса авиационная',
                'NPT': 'National Pipe Taper коническая американская',
                'ORFS': 'O-Ring Face Seal плоское уплотнение кольцо',
            }
            if standard in synonyms:
                parts.append(synonyms[standard])

        thread = art.get('thread')
        if thread:
            parts.append(f"Резьба {thread}")

        armature = art.get('armature')
        if armature:
            parts.append(f"Тип {armature}")
            if 'male' in str(armature).lower():
                parts.extend(['штуцер', 'наружная резьба', 'папа', 'наружный'])
            if 'female' in str(armature).lower():
                parts.extend(['гайка', 'внутренняя резьба', 'мама', 'внутренний'])

        angle = art.get('angle')
        if angle is not None:
            parts.append(f"Угол {angle} градусов")
            if angle == 90:
                parts.extend(['уголок', 'угловой', 'прямой угол', 'перпендикулярный'])
            elif angle == 45:
                parts.extend(['полу уголок', 'угол 45'])
            elif angle == 0:
                parts.extend(['прямой', 'прямое соединение', 'прямой фитинг'])

        dy = art.get('dy')
        if dy:
            parts.append(f"Диаметр Dy {dy} мм для рукава {dy}")

        comp_type = art.get('component_type') or self._infer_component_type(art)
        if comp_type:
            parts.append(comp_type)
            synonyms_type = {
                'fitting': 'фитинг соединитель шланговый',
                'adapter': 'переходник адаптер футорка',
                'plug': 'заглушка пробка колпачок',
            }
            if comp_type in synonyms_type:
                parts.append(synonyms_type[comp_type])

        return '. '.join(filter(None, parts))

    def _infer_component_type(self, art: dict) -> Optional[str]:
        """Определение типа компонента по данным."""
        name = art.get('name', '').lower()
        article = art.get('article', '').lower()

        if 'переходник' in name or 'adapter' in name or article.startswith('2'):
            return 'adapter'
        if 'заглушка' in name or 'пробка' in name or 'plug' in name:
            return 'plug'
        if 'фитинг' in name or 'fitting' in name or article.startswith('1'):
            return 'fitting'

        return 'unknown'

    def search(self, query: str, top_k: int = None):
        """Основной метод поиска."""
        start_time = time.time()

        if top_k is None:
            top_k = self.config.top_k_return

        # 1. Retrieval
        candidates = self._retrieve_candidates(query)

        # 2. Extraction через OpenRouter
        extracted = self._extract_parameters(query)

        # 3. Reranking
        results = self._rerank_candidates(candidates, extracted, top_k)

        processing_time = (time.time() - start_time) * 1000

        return results, processing_time

    def _retrieve_candidates(self, query: str) -> List[Dict[str, Any]]:
        """Поиск кандидатов в векторной БД."""
        query_embedding = self.embedder.encode([query]).tolist()[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.config.top_k_retrieve,
            include=["metadatas", "distances", "documents"]
        )

        candidates = []
        for meta, distance, doc in zip(
            results['metadatas'][0],
            results['distances'][0],
            results['documents'][0]
        ):
            similarity = max(0.0, min(1.0, 1.0 / (1.0 + distance)))
            candidates.append({
                'article': Article(**meta),
                'similarity': similarity,
                'matched_text': doc
            })

        return candidates

    def _extract_parameters(self, query: str) -> ExtractedParams:
        """Извлечение параметров через OpenRouter."""
        user_prompt = self.extraction_template.format(
            system_prompt=self.system_prompt,
            user_query=query
        )

        try:
            raw_response = self.llm.generate(
                system_prompt="Ты — инженер по гидравлике. Отвечай только JSON без пояснений.",
                user_prompt=user_prompt,
                temperature=0.05
            )

            params_dict = self.llm._parse_json_from_text(raw_response)

        except Exception as e:
            print(f"Ошибка извлечения через OpenRouter: {e}")
            params_dict = {}

        return self._validate_params(params_dict)

    def _validate_params(self, raw: dict) -> ExtractedParams:
        """Валидация и очистка извлечённых параметров."""

        # Стандарт
        standard = raw.get('standard')
        if standard:
            standard_upper = str(standard).upper()
            if standard_upper not in self.VALID_STANDARDS:
                for valid in self.VALID_STANDARDS:
                    if valid in standard_upper or standard_upper in valid:
                        standard = valid
                        break
                else:
                    standard = None

        # Тип соединения
        armature = raw.get('armature')
        if armature:
            arm_lower = str(armature).lower()
            if 'пап' in arm_lower or 'штуц' in arm_lower or 'наруж' in arm_lower:
                armature = 'male'
            elif 'мам' in arm_lower or 'гайк' in arm_lower or 'внутр' in arm_lower:
                armature = 'female'
            elif arm_lower not in self.VALID_ARMATURES:
                armature = None

        # Угол
        angle = raw.get('angle')
        if angle is not None:
            try:
                angle = int(angle)
                if angle not in self.VALID_ANGLES:
                    angle = min(self.VALID_ANGLES, key=lambda x: abs(x - angle))
            except (ValueError, TypeError):
                angle = None

        # Диаметр
        dy = raw.get('dy')
        if dy is not None:
            try:
                dy = int(dy)
                if not (4 <= dy <= 50):
                    dy = None
            except (ValueError, TypeError):
                dy = None

        # Резьба
        thread = raw.get('thread')
        if thread and not isinstance(thread, str):
            thread = None

        # Тип компонента
        comp_type = raw.get('component_type')
        if comp_type:
            type_lower = str(comp_type).lower()
            if 'фитинг' in type_lower or 'fitting' in type_lower:
                comp_type = 'fitting'
            elif 'переход' in type_lower or 'адаптер' in type_lower or 'adapter' in type_lower:
                comp_type = 'adapter'
            elif 'заглушк' in type_lower or 'пробк' in type_lower or 'plug' in type_lower:
                comp_type = 'plug'
            elif type_lower not in self.VALID_TYPES:
                comp_type = None

        return ExtractedParams(
            standard=standard,
            thread=thread,
            armature=armature,
            angle=angle,
            dy=dy,
            component_type=comp_type,
            confidence=raw.get('confidence', 'medium')
        )

    def _rerank_candidates(
        self,
        candidates: List[Dict],
        extracted: ExtractedParams,
        top_k: int
    ) -> List[SearchResult]:
        """Переранжирование с учётом извлечённых параметров."""

        scored = []

        for cand in candidates:
            art = cand['article']
            base_score = max(0.0, min(1.0, cand['similarity']))
            bonus = 0.0
            matches = []

            if extracted.standard and art.standard:
                if extracted.standard.upper() == art.standard.upper():
                    bonus += 0.30
                    matches.append(f"стандарт:{art.standard}")
                elif extracted.standard in str(art.standard).upper():
                    bonus += 0.15

            if extracted.thread and art.thread:
                if self._thread_matches(extracted.thread, art.thread):
                    bonus += 0.25
                    matches.append(f"резьба:{art.thread}")

            if extracted.armature and art.armature:
                if extracted.armature.lower() in str(art.armature).lower():
                    bonus += 0.20
                    matches.append(f"тип:{art.armature}")

            if extracted.angle is not None and art.angle is not None:
                if extracted.angle == art.angle:
                    bonus += 0.15
                    matches.append(f"угол:{art.angle}°")

            if extracted.dy is not None and art.dy is not None:
                if extracted.dy == art.dy:
                    bonus += 0.10
                    matches.append(f"Dy:{art.dy}")

            if extracted.component_type and self._infer_component_type(art.__dict__):
                inferred = self._infer_component_type(art.__dict__)
                if extracted.component_type != inferred:
                    bonus -= 0.05

            final_score = min(base_score + bonus, 1.0)

            scored.append({
                'article': art,
                'score': final_score,
                'base_similarity': base_score,
                'parameter_matches': matches,
                'extracted': extracted
            })

        scored.sort(key=lambda x: x['score'], reverse=True)

        results = []
        for s in scored[:top_k]:
            results.append(SearchResult(
                article=s['article'].article,
                name=s['article'].name,
                description=s['article'].description,
                confidence=s['score'],
                base_similarity=s['base_similarity'],
                parameter_matches=s['parameter_matches'],
                extracted_params={
                    'standard': extracted.standard,
                    'thread': extracted.thread,
                    'armature': extracted.armature,
                    'angle': extracted.angle,
                    'dy': extracted.dy,
                    'component_type': extracted.component_type,
                    'confidence': extracted.confidence
                }
            ))

        return results

    def _thread_matches(self, query_thread: str, article_thread: str) -> bool:
        """Нечёткое сопоставление резьб."""
        q = str(query_thread).lower().replace('x', '×').replace('*', '×').replace(' ', '')
        a = str(article_thread).lower().replace('x', '×').replace('*', '×').replace(' ', '')

        if q == a:
            return True

        if 'm' in q and 'm' in a:
            q_norm = q.replace('м', 'm').replace('х', 'x').replace('×', 'x')
            a_norm = a.replace('м', 'm').replace('х', 'x').replace('×', 'x')
            if q_norm == a_norm:
                return True

        if '/' in q and '/' in a:
            try:
                q_num = eval(q.split('-')[0].split('m')[0])
                a_num = eval(a.split('-')[0].split('m')[0])
                return abs(q_num - a_num) < 0.01
            except:
                pass

        return False

    def get_stats(self) -> dict:
        """Статистика сервиса."""
        return {
            'total_articles': self.collection.count(),
            'embedding_dim': self.embedding_dim,
            'embedding_model': self.config.embedding_model,
            'llm_provider': 'openrouter',
            'llm_model': self.config.openrouter_model,
        }