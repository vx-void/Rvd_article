from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database.models.base_component import HydraulicComponent
from database.models.reference.ref_standard import RefStandard
from database.models.reference.ref_thread import RefThread
from database.models.reference.ref_armature import RefArmature


class Plug(HydraulicComponent):
    __tablename__ = "plugs"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    article = Column(String, nullable=False)
    name = Column(String)

    standard_id = Column(Integer, ForeignKey("reference.ref_standard.id"))
    thread_id = Column(Integer, ForeignKey("reference.ref_thread.id"))
    armature_id = Column(Integer, ForeignKey("reference.ref_armature.id"))
    s_key = Column(String)

    standard = relationship(RefStandard)
    thread = relationship(RefThread)
    armature = relationship(RefArmature)
