from sqlalchemy import Column, Integer, String



class RefSeria():
    __tablename__ = "ref_series"
    __table_args__ = {"schema": "reference"}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
