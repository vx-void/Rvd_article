from sqlalchemy import Column, Integer, String


class HydraulicComponent():
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    article = Column(Integer, nullable=False)
    name = Column(String, nullable=False)