from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from backend.database.models.base_component import HydraulicComponent
from backend.database.models.reference.ref_standard import RefStandard
from backend.database.models.reference.ref_thread import RefThread
from backend.database.models.reference.ref_armature import RefArmature
from backend.database.models.reference.ref_angle import RefAngle
from backend.database.models.reference.ref_seria import RefSeria


class Fitting(HydraulicComponent):
    __tablename__ = "fittings"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    article = Column(String, nullable=False)
    name = Column(String)

    standard_id = Column(Integer, ForeignKey("reference.ref_standard.id"))
    dy = Column(Integer)
    thread_id = Column(Integer, ForeignKey("reference.ref_thread.id"))
    armature_id = Column(Integer, ForeignKey("reference.ref_armature.id"))
    angle_id = Column(Integer, ForeignKey("reference.ref_angle.id"))
    series_id = Column(Integer, ForeignKey("reference.ref_series.id"))

    usit = Column(Boolean)
    o_ring = Column(Boolean)
    s_key = Column(String)

    standard = relationship(RefStandard)
    thread = relationship(RefThread)
    armature = relationship(RefArmature)
    angle = relationship(RefAngle)
    series = relationship(RefSeria)
