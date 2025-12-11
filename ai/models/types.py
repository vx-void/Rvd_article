
from typing import TypedDict, Optional, Literal, Union
from dataclasses import dataclass
from enum import Enum


class ComponentType(str, Enum):
    FITTINGS = "fittings"
    ADAPTERS = "adapters"
    PLUGS = "plugs"
    ADAPTER_TEE = "adapter-tee"
    BANJO = "banjo"
    BANJO_BOLT = "banjo-bolt"
    BRS = "brs"
    COUPLING = "coupling"


class ArmatureType(str, Enum):
    NUT = "гайка"
    UNION = "штуцер"
    CONICAL_UNION = "штуцер конусный"


@dataclass
class BaseComponent:
    component_type: ComponentType
    original_query: str
    timestamp: str


@dataclass
class FittingData:
    standard: str
    Dy: Optional[int] = None
    thread: Optional[str] = None
    armature: Optional[ArmatureType] = None
    seria: Optional[str] = None
    angle: int = 0
    removable_nut: bool = False
    unstandard_thread: bool = False
    D_out: Optional[int] = None
    usit: Optional[bool] = None
    s_key: Optional[str] = None
    compact: Optional[bool] = None
    pin: Optional[bool] = None
    o_ring: Optional[bool] = None
    long: Optional[int] = None


@dataclass
class AdapterData:
    standard_1: str
    standard_2: str
    thread_1: str
    thread_2: str
    armature_1: Optional[ArmatureType] = None
    armature_2: Optional[ArmatureType] = None
    angle: int = 0
    s_key: Optional[str] = None


@dataclass
class PlugData:
    standard: str
    thread_type: str
    thread: str
    armature: Optional[ArmatureType] = None
    s_key: Optional[str] = None


@dataclass
class AdapterTeeData:
    standard_1: str
    standard_2: str
    standard_3: str
    thread_1: str
    thread_2: str
    thread_3: str
    armature_1: Optional[ArmatureType] = None
    armature_2: Optional[ArmatureType] = None
    armature_3: Optional[ArmatureType] = None



STANDARD_DY_VALUES = [4, 5, 6, 8, 10, 12, 16, 20, 25, 32, 38, 50]