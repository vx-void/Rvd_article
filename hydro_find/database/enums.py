# hydro_find/database/enums.py

from enum import IntEnum

class Standard(IntEnum):
    BSP = 1
    BSPT = 2
    JIC = 3
    DKOL = 4
    DKOS = 5
    NPTF = 6
    ORFS = 7
    # ... добавить остальные из CSV

class Thread(IntEnum):
    # Пример: можно использовать ID = хэш строки или порядковый номер
    # Но лучше пронумеровать вручную, как в CSV
    # "1" → 1, "3/4" → 2, "1.5" → 3 и т.д.
    # Для упрощения — можно использовать строку в модели, но для Enum ID = индекс в списке
    BSP_1 = 1
    BSP_3_4 = 2
    BSP_1_1_4 = 3
    JIC_1_2 = 4
    JIC_3_4 = 5
    # ... (реализуется на основе CSV)

class Armature(IntEnum):
    NUT = 1        # "гайка"
    UNION = 2      # "штуцер"
    CONICAL_UNION = 3  # "штуцер конусный"

class Angle(IntEnum):
    ANGLE_0 = 0
    ANGLE_45 = 45
    ANGLE_90 = 90

class Series(IntEnum):
    LIGHT = 1      # "легкая"
    HEAVY = 2      # "тяжелая"
    INTERLOCK = 3  # "interlock"

# ... остальные Enum'ы по необходимости