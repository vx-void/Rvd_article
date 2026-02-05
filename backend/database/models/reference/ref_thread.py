from sqlalchemy import Column, Integer, String



class RefThread():
    __tablename__ = "ref_thread"
    __table_args__ = {"schema": "reference"}

    id = Column(Integer, primary_key=True)
    designation = Column(String, nullable=False)
