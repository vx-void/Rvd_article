# hydro_find/database/repository.py

from typing import List, Dict, Any, Optional
import logging

from .connection import DatabaseConnection
from .models import CATEGORY_TO_MODEL
from .query_builder import ComponentQueryBuilder

logger = logging.getLogger(__name__)


class ComponentRepository:
    def __init__(self, db: DatabaseConnection):
        self._db = db

    def search(self, params: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Поиск компонентов по параметрам"""
        category = params.get("component_type")
        if not category:
            logger.warning("No component type specified")
            return []

        model_class = CATEGORY_TO_MODEL.get(category)
        if not model_class:
            logger.warning(f"Unknown component type: {category}")
            return []

        try:
            # Использование контекстного менеджера для сессии
            with self._db.get_session() as session:
                query = session.query(model_class)
                builder = ComponentQueryBuilder(query, params)
                results = builder.build().limit(limit).all()

                # Преобразование результатов
                return [self._enrich_component_data(item.to_dict()) for item in results]

        except Exception as e:
            logger.error(f"Database search error: {e}")
            return []

    def get_by_article(self, category: str, article: str) -> Optional[Dict[str, Any]]:
        """Получение компонента по артикулу"""
        model_class = CATEGORY_TO_MODEL.get(category)
        if not model_class:
            return None

        try:
            with self._db.get_session() as session:
                item = session.query(model_class).filter(
                    model_class.article == article
                ).first()

                return self._enrich_component_data(item.to_dict()) if item else None

        except Exception as e:
            logger.error(f"Error getting component by article: {e}")
            return None

    def _enrich_component_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Добавляет дополнительную информацию к данным компонента"""
        # Можно добавить вычисляемые поля или форматирование
        if 'article' in data:
            data['article_formatted'] = f"ART-{data['article']}"
        return data