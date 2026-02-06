from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


from backend.database.models.base_component import HydraulicComponent
from backend.database.models.reference.ref_standard import RefStandard
from backend.database.models.reference.ref_thread import RefThread
from backend.database.models.reference.ref_armature import RefArmature


class AdapterTee(HydraulicComponent):
    __tablename__ = "adapter_tee"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    article = Column(String, nullable=False)
    name = Column(String)

    standard_1_id = Column(Integer, ForeignKey("reference.ref_standard.id"))
    standard_2_id = Column(Integer, ForeignKey("reference.ref_standard.id"))
    standard_3_id = Column(Integer, ForeignKey("reference.ref_standard.id"))

    thread_1_id = Column(Integer, ForeignKey("reference.ref_thread.id"))
    thread_2_id = Column(Integer, ForeignKey("reference.ref_thread.id"))
    thread_3_id = Column(Integer, ForeignKey("reference.ref_thread.id"))

    armature_1_id = Column(Integer, ForeignKey("reference.ref_armature.id"))
    armature_2_id = Column(Integer, ForeignKey("reference.ref_armature.id"))
    armature_3_id = Column(Integer, ForeignKey("reference.ref_armature.id"))

    standard_1 = relationship(RefStandard, foreign_keys=[standard_1_id])
    standard_2 = relationship(RefStandard, foreign_keys=[standard_2_id])
    standard_3 = relationship(RefStandard, foreign_keys=[standard_3_id])

    thread_1 = relationship(RefThread, foreign_keys=[thread_1_id])
    thread_2 = relationship(RefThread, foreign_keys=[thread_2_id])
    thread_3 = relationship(RefThread, foreign_keys=[thread_3_id])

    armature_1 = relationship(RefArmature, foreign_keys=[armature_1_id])
    armature_2 = relationship(RefArmature, foreign_keys=[armature_2_id])
    armature_3 = relationship(RefArmature, foreign_keys=[armature_3_id])
