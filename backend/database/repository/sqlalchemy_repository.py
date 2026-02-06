from sqlalchemy.orm import Session
from backend.database.filters.component_filter import ComponentFilter
from backend.database.interfaces.repository import IComponentRepository


class SqlAlchemyComponentRepository(IComponentRepository):

    def __init__(self, session: Session):
        self.session = session

    def find(self, filters: ComponentFilter):
        model = filters.component_type
        query = self.session.query(model)

        for field, value in filters.params.items():
            if value is None:
                continue

            column = getattr(model, field)
            query = query.filter(column == value)

        return query.all()
