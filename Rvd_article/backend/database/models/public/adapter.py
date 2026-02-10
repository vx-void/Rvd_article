from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Nullable
from sqlalchemy.orm import relationship

from database.models.base_component import HydraulicComponent
from database.models.reference.ref_standard import RefStandard
from database.models.reference.ref_thread import RefThread
from database.models.reference.ref_armature import RefArmature
from database.models.reference.ref_angle import RefAngle



class Adapter(HydraulicComponent):
    __tablename__ = "adapters"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    article = Column(String, nullable=False)
    name = Column(String)

    standard_1_id = Column(Integer, ForeignKey("reference.ref_standard.id"))
    thread_1_id = Column(Integer, ForeignKey("reference.ref_thread.id"))
    armature_1_id = Column(Integer, ForeignKey("reference.ref_armature.id"))

    standard_2_id = Column(Integer, ForeignKey("reference.ref_standard.id"))
    thread_2_id = Column(Integer, ForeignKey("reference.ref_thread.id"))
    armature_2_id = Column(Integer, ForeignKey("reference.ref_armature.id"))

    s_key = Column(Integer, nullable=True)
    counter_nut = Column(Boolean, nullable=False, default=False)
    angle_id = Column(Integer, ForeignKey("reference.ref_angle"))


    standard_1 = relationship(RefStandard)
    standard_2 = relationship(RefStandard)
    thread_1 = relationship(RefThread)
    thread_2 = relationship(RefThread)
    armature_1 = relationship(RefArmature)
    armature_2 = relationship(RefArmature)
    angle = relationship(RefAngle)
