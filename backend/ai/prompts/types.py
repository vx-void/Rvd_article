# ../ai/types.py

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


class PreprocessingTask(str, Enum):
    CLASSIFY = "classify"
    QUANTITY = "quantity"
    SPLIT = "split"