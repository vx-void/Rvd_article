
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

STANDARD_DY_VALUES = [4, 5, 6, 8, 10, 12, 16, 20, 25, 32, 38, 50]