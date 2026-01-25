# backend/app/database/models.py

from sqlalchemy import Column, Integer, String, Boolean, SmallInteger, ForeignKey
from .connection import Base
from .reference import Standard, Armature, Angle, Series, Thread

class ComponentBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    article = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

class Fitting(ComponentBase):
    __tablename__ = "fittings"

    standard_id = Column(Integer)
    thread_id = Column(Integer)
    armature_id = Column(Integer)
    angle_id = Column(Integer)
    seria_id = Column(Integer)

    Dy = Column(Integer)
    usit = Column(Boolean, default=False)
    o_ring = Column(Boolean, default=False)
    s_key = Column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "article": self.article,
            "name": self.name,
            "standard": Standard(self.standard_id).name if self.standard_id else None,
            "thread": Thread(self.thread_id).name if self.thread_id else None,
            "armature": Armature(self.armature_id).name if self.armature_id else None,
            "angle": Angle(self.angle_id).name if self.angle_id else None,
            "seria": Series(self.seria_id).name if self.seria_id else None,
            "Dy": self.Dy,
            "usit": self.usit,
            "o_ring": self.o_ring,
            "s_key": self.s_key
        }

class Adapter(ComponentBase):
    __tablename__ = "adapters"

    standard_1_id = Column(Integer)
    standard_2_id = Column(Integer)
    thread_1_id = Column(Integer)
    thread_2_id = Column(Integer)
    armature_1_id = Column(Integer)
    armature_2_id = Column(Integer)
    angle_id = Column(Integer)
    s_key = Column(String)
    counter_nut = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "article": self.article,
            "name": self.name,
            "standard_1": Standard(self.standard_1_id).name if self.standard_1_id else None,
            "standard_2": Standard(self.standard_2_id).name if self.standard_2_id else None,
            "thread_1": Thread(self.thread_1_id).name if self.thread_1_id else None,
            "thread_2": Thread(self.thread_2_id).name if self.thread_2_id else None,
            "armature_1": Armature(self.armature_1_id).name if self.armature_1_id else None,
            "armature_2": Armature(self.armature_2_id).name if self.armature_2_id else None,
            "angle": Angle(self.angle_id).name if self.angle_id else None,
            "s_key": self.s_key,
            "counter_nut": self.counter_nut
        }

class Plug(ComponentBase):
    __tablename__ = "plugs"

    standard_id = Column(Integer)
    thread_id = Column(Integer)
    armature_id = Column(Integer)
    s_key = Column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "article": self.article,
            "name": self.name,
            "standard": Standard(self.standard_id).name if self.standard_id else None,
            "thread": Thread(self.thread_id).name if self.thread_id else None,
            "armature": Armature(self.armature_id).name if self.armature_id else None,
            "s_key": self.s_key
        }

class AdapterTee(ComponentBase):
    __tablename__ = "adapter_tees"

    standard_1_id = Column(Integer)
    standard_2_id = Column(Integer)
    standard_3_id = Column(Integer)
    thread_1_id = Column(Integer)
    thread_2_id = Column(Integer)
    thread_3_id = Column(Integer)
    armature_1_id = Column(Integer)
    armature_2_id = Column(Integer)
    armature_3_id = Column(Integer)
    s_key = Column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "article": self.article,
            "name": self.name,
            "standard_1": Standard(self.standard_1_id).name if self.standard_1_id else None,
            "standard_2": Standard(self.standard_2_id).name if self.standard_2_id else None,
            "standard_3": Standard(self.standard_3_id).name if self.standard_3_id else None,
            "thread_1": Thread(self.thread_1_id).name if self.thread_1_id else None,
            "thread_2": Thread(self.thread_2_id).name if self.thread_2_id else None,
            "thread_3": Thread(self.thread_3_id).name if self.thread_3_id else None,
            "armature_1": Armature(self.armature_1_id).name if self.armature_1_id else None,
            "armature_2": Armature(self.armature_2_id).name if self.armature_2_id else None,
            "armature_3": Armature(self.armature_3_id).name if self.armature_3_id else None,
            "s_key": self.s_key
        }

class Banjo(ComponentBase):
    __tablename__ = "banjo"

    standard_id = Column(Integer)
    Dy = Column(Integer)
    thread_id = Column(Integer)
    seria_id = Column(Integer)
    thread_type = Column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "article": self.article,
            "name": self.name,
            "standard": Standard(self.standard_id).name if self.standard_id else None,
            "Dy": self.Dy,
            "thread": Thread(self.thread_id).name if self.thread_id else None,
            "seria": Series(self.seria_id).name if self.seria_id else None,
            "thread_type": self.thread_type
        }

class BRS(ComponentBase):
    __tablename__ = "brs"

    standard_id = Column(Integer)
    break_type = Column(String)
    locknut = Column(Boolean, default=False)
    dn = Column(Integer)
    type = Column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "article": self.article,
            "name": self.name,
            "standard": Standard(self.standard_id).name if self.standard_id else None,
            "break_type": self.break_type,
            "locknut": self.locknut,
            "dn": self.dn,
            "type": self.type
        }

class Coupling(ComponentBase):
    __tablename__ = "couplings"

    standard_id = Column(Integer)
    thread_id = Column(Integer)
    Dy = Column(Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "article": self.article,
            "name": self.name,
            "standard": Standard(self.standard_id).name if self.standard_id else None,
            "thread": Thread(self.thread_id).name if self.thread_id else None,
            "Dy": self.Dy
        }

CATEGORY_TO_MODEL = {
    "fittings": Fitting,
    "adapters": Adapter,
    "plugs": Plug,
    "adapter-tee": AdapterTee,
    "banjo": Banjo,
    "brs": BRS,
    "coupling": Coupling,
}