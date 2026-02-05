from sqlalchemy import Column, Integer, String



class RefAngle():
    __tablename__ = "ref_angle"
    __table_args__ = {"schema": "reference"}

    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)
