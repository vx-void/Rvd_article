# backend/app/database/query_build.py

from typing import Dict, Any
from sqlalchemy import and_, or_
from sqlalchemy.orm import Query
import logging
from .models import Fitting, Adapter, Plug, AdapterTee, Banjo, BRS, Coupling
from .enums import Standard, Armature, Angle, Series, Thread

logger = logging.getLogger(__name__)


class ComponentQueryBuilder:
    def __init__(self, query: Query, params: Dict[str, Any]):
        self.query = query
        self.params = params
        if self.query.column_descriptions:
            self.model = self.query.column_descriptions[0]['entity']
        else:
            self.model = None

    def build(self) -> Query:
        """Создает запрос с применением всех фильтров"""
        try:
            return (
                self._apply_exact_filters()
                ._apply_text_search()
                .query
            )
        except Exception as e:
            logger.error(f"Error building query: {e}")
            return self.query

    def _apply_exact_filters(self):
        params = self.params

        if not self.model:
            return self

        # Добавлена проверка существования полей
        filter_handlers = {
            'standard': self._apply_standard_filter,
            'armature': self._apply_armature_filter,
            'thread': self._apply_thread_filter,
            'angle': self._apply_angle_filter,
            'seria': self._apply_seria_filter,
        }

        for param_name, handler in filter_handlers.items():
            if param_name in params:
                handler(params[param_name])


        for flag in ['usit', 'o_ring', 'counter_nut', 'locknut']:
            if flag in params and params[flag] is not None:
                self._apply_boolean_filter(flag, params[flag])

        # Числовые фильтры
        if 'Dy' in params and params['Dy'] is not None and hasattr(self.model, 'Dy'):
            self.query = self.query.filter(self.model.Dy == params['Dy'])

        return self

    def _apply_standard_filter(self, standard_value):
        try:
            std_enum = getattr(Standard, standard_value.upper().strip(), None)
            if not std_enum:
                return

            if hasattr(self.model, 'standard_id'):
                self.query = self.query.filter(self.model.standard_id == std_enum.value)
            elif hasattr(self.model, 'standard_1_id'):
                self.query = self.query.filter(
                    or_(
                        self.model.standard_1_id == std_enum.value,
                        self.model.standard_2_id == std_enum.value
                    )
                )
        except Exception as e:
            logger.warning(f"Failed to apply standard filter: {e}")

    def _apply_boolean_filter(self, field_name, value):

        try:
            if hasattr(self.model, field_name):
                bool_value = str(value).lower() in ['true', '1', 'yes', 'y']
                self.query = self.query.filter(getattr(self.model, field_name) == bool_value)
        except Exception as e:
            logger.warning(f"Failed to apply boolean filter {field_name}: {e}")




    # ... остальные методы фильтрации ...

    def _apply_text_search(self):
        """Применяет текстовый поиск по артикулу и названию"""
        if not self.model:
            return self

        original_query = self.params.get("original_query", "")
        terms = [t.strip() for t in original_query.split() if t.strip()]

        if terms:
            try:
                conditions = []
                for term in terms:
                    # Добавляем поиск по каждому полю
                    if hasattr(self.model, 'article'):
                        conditions.append(self.model.article.ilike(f"%{term}%"))
                    if hasattr(self.model, 'name'):
                        conditions.append(self.model.name.ilike(f"%{term}%"))
                    if hasattr(self.model, 's_key'):
                        conditions.append(self.model.s_key.ilike(f"%{term}%"))

                if conditions:
                    self.query = self.query.filter(or_(*conditions))
            except Exception as e:
                logger.error(f"Error in text search: {e}")

        return self