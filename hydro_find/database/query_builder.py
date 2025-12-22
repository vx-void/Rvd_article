from typing import Dict, Any
from sqlalchemy import and_, or_
from sqlalchemy.orm import Query
from .models import Fitting, Adapter, Plug, AdapterTee, Banjo, BRS, Coupling
from .enums import Standard, Armature, Angle, Series, Thread

class ComponentQueryBuilder:
    def __init__(self, query: Query, params: Dict[str, Any]):
        self.query = query
        self.params = params
        self.model = self.query.column_descriptions[0]['entity']

    def build(self) -> Query:
        return (
            self._apply_exact_filters()
                ._apply_text_search()
                .query
        )

    def _apply_exact_filters(self):
        params = self.params

        if 'standard' in params:
            try:
                std_enum = getattr(Standard, params['standard'].upper(), None)
                if std_enum:
                    if hasattr(self.model, 'standard_id'):
                        self.query = self.query.filter(self.model.standard_id == std_enum.value)
                    elif hasattr(self.model, 'standard_1_id'):
                        self.query = self.query.filter(
                            or_(self.model.standard_1_id == std_enum.value, self.model.standard_2_id == std_enum.value)
                        )
            except (AttributeError, ValueError):
                pass

        if 'armature' in params:
            try:
                arm_enum = getattr(Armature, params['armature'].upper().replace(' ', '_'), None)
                if arm_enum:
                    if hasattr(self.model, 'armature_id'):
                        self.query = self.query.filter(self.model.armature_id == arm_enum.value)
                    elif hasattr(self.model, 'armature_1_id'):
                        self.query = self.query.filter(
                            or_(self.model.armature_1_id == arm_enum.value, self.model.armature_2_id == arm_enum.value)
                        )
            except (AttributeError, ValueError):
                pass

        if 'thread' in params:
            try:
                thread_enum = Thread.from_string(params['thread'])
                if hasattr(self.model, 'thread_id'):
                    self.query = self.query.filter(self.model.thread_id == thread_enum.value)
                elif hasattr(self.model, 'thread_1_id'):
                    self.query = self.query.filter(
                        or_(self.model.thread_1_id == thread_enum.value, self.model.thread_2_id == thread_enum.value)
                    )
            except (AttributeError, ValueError):
                pass

        if 'angle' in params:
            try:
                angle_enum = getattr(Angle, f"ANGLE_{params['angle']}", None)
                if angle_enum and hasattr(self.model, 'angle_id'):
                    self.query = self.query.filter(self.model.angle_id == angle_enum.value)
            except (AttributeError, ValueError):
                pass

        if 'seria' in params:
            try:
                seria_enum = getattr(Series, params['seria'].upper().replace('-', '_'), None)
                if seria_enum and hasattr(self.model, 'seria_id'):
                    self.query = self.query.filter(self.model.seria_id == seria_enum.value)
            except (AttributeError, ValueError):
                pass

        for flag in ['usit', 'o_ring', 'counter_nut', 'locknut']:
            if flag in params and hasattr(self.model, flag):
                self.query = self.query.filter(getattr(self.model, flag) == params[flag])

        if 'Dy' in params and hasattr(self.model, 'Dy'):
            self.query = self.query.filter(self.model.Dy == params['Dy'])

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