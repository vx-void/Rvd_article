from sqlalchemy import Column, Integer, String



class RefArmature():
    __tablename__ = "ref_thread"
    __table_args__ = {"schema": "reference"}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    abbriveatury=Column(String, nullable=False)