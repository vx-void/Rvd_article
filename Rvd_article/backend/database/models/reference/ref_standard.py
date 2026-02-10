from sqlalchemy import Column, Integer, String


class RefStandard():
    __tablename__ = "ref_standard"
    __table_args__ = {"schema": "reference"}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
