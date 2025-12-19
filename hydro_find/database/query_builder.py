# hydro_find/database/query_builder.py

from typing import Dict, Any
from sqlalchemy import and_, or_
from sqlalchemy.orm import Query
from .models import Fitting, Adapter, Plug, AdapterTee
from .enums import Standard, Armature, Angle, Series

CATEGORY_TO_MODEL = {
    "fittings": Fitting,
    "adapters": Adapter,
    "plugs": Plug,
    "adapter-tee": AdapterTee,
}

class ComponentQueryBuilder:
    """
    Формирует безопасные, параметризованные SQL-запросы
    на основе нормализованных параметров от ИИ.
    Теперь с числовыми FK (Enum.value) — без JOIN.
    """

    def __init__(self, query: Query, params: Dict[str, Any]):
        self.query = query
        self.params = params
        self.model = self.query.column_descriptions[0]['entity']

    def build(self) -> Query:
        return (
            self._apply_exact_filters()
                ._apply_fuzzy_filters()
                ._apply_text_search()
                .query
        )

    def _apply_exact_filters(self):
        params = self.params

        # Фильтрация по Enum'ам (FK как числа)
        if 'standard' in params:
            std_enum = getattr(Standard, params['standard'].upper(), None)
            if std_enum:
                if hasattr(self.model, 'standard_id'):
                    self.query = self.query.filter(self.model.standard_id == std_enum.value)
                elif hasattr(self.model, 'standard_1_id'):  # adapters, adapter-tees
                    self.query = self.query.filter(
                        or_(self.model.standard_1_id == std_enum.value, self.model.standard_2_id == std_enum.value)
                    )

        if 'armature' in params:
            arm_enum = getattr(Armature, params['armature'].upper().replace(' ', '_'), None)
            if arm_enum:
                if hasattr(self.model, 'armature_id'):
                    self.query = self.query.filter(self.model.armature_id == arm_enum.value)
                elif hasattr(self.model, 'armature_1_id'):
                    self.query = self.query.filter(
                        or_(self.model.armature_1_id == arm_enum.value, self.model.armature_2_id == arm_enum.value)
                    )

        if 'angle' in params:
            angle_enum = getattr(Angle, f"ANGLE_{params['angle']}", None)
            if angle_enum and hasattr(self.model, 'angle_id'):
                self.query = self.query.filter(self.model.angle_id == angle_enum.value)

        if 'seria' in params:
            seria_enum = getattr(Series, params['seria'].upper().replace('-', '_'), None)
            if seria_enum and hasattr(self.model, 'seria_id'):
                self.query = self.query.filter(self.model.seria_id == seria_enum.value)

        # Булевы флаги
        for flag in ['usit', 'o_ring', 'locknut']:
            if flag in params and hasattr(self.model, flag):
                self.query = self.query.filter(getattr(self.model, flag) == params[flag])

        # Dy (только если есть в модели)
        if 'Dy' in params and hasattr(self.model, 'Dy'):
            self.query = self.query.filter(self.model.Dy == params['Dy'])

        return self

    def _apply_fuzzy_filters(self):
        # Для thread — фильтрация по строковому полю (если оно есть в модели)
        # thread_id в БД — это ID из справочника, но в модели может храниться как строка
        # или преобразовываться в ID по ходу дела.
        # Если thread_id — строка, то:
        if 'thread' in self.params and hasattr(self.model, 'thread_id'):
            # Предположим, thread_id — это строка в модели (для простоты)
            # Или если у вас есть справочник резьб: thread_name_to_id = {"1": 1, "3/4": 2...}
            # thread_id = thread_name_to_id.get(self.params['thread'])
            # self.query = self.query.filter(self.model.thread_id == thread_id)
            pass  # Реализуется отдельно, если thread_id — строка
        return self

    def _apply_text_search(self):
        if original_query := self.params.get("original_query"):
            terms = [t.strip() for t in original_query.split() if t.strip()]
            if terms:
                conditions = [
                    or_(
                        self.model.article.ilike(f"%{term}%"),
                        self.model.name.ilike(f"%{term}%")
                    )
                    for term in terms
                ]
                self.query = self.query.filter(and_(*conditions))
        return self