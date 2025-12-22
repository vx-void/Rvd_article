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
    BANJO = 8

class Thread(IntEnum):

    _1_8 = 1       # "1/8"
    _1_4 = 2       # "1/4"
    _3_8 = 3       # "3/8"
    _1_2 = 4       # "1/2"
    _3_4 = 5       # "3/4"
    _1 = 6         # "1"
    _1_1_4 = 7     # "1.1/4"
    _1_1_2 = 8     # "1.1/2"
    _2 = 9         # "2"
    # Метрические
    M14_X_1_5 = 10 # "14х1.5"
    M16_X_1_5 = 11 # "16х1.5"
    M18_X_1_5 = 12 # "18х1.5"
    # Дробные дюймы и др.
    _1_3_16 = 13   # "1,3/16"
    _1_5_16 = 14   # "1,5/16"
    _1_5_8 = 15    # "1,5/8"
    _1_7_8 = 16    # "1,7/8"
    _2_1_2 = 17    # "2,1/2"
    _5_8 = 18      # "5/8"
    _7_8 = 19      # "7/8"
    _9_16 = 20     # "9/16"
    _5_16 = 21     # "5/16"
    _7_16 = 22     # "7/16"

    _3_4_INCH = 23 # "3/4''"


    @classmethod
    def from_string(cls, value: str) -> 'Thread':
        """
        Возвращает Enum-значение по строке из CSV.
        Если строка не найдена — выбрасывает ValueError.
        """
        # Словарь сопоставления строк и ID
        mapping = {
            "1/8": cls._1_8,
            "1/4": cls._1_4,
            "3/8": cls._3_8,
            "1/2": cls._1_2,
            "3/4": cls._3_4,
            "1": cls._1,
            "1.1/4": cls._1_1_4,
            "1.1/2": cls._1_1_2,
            "2": cls._2,
            "14х1.5": cls.M14_X_1_5,
            "16х1.5": cls.M16_X_1_5,
            "18х1.5": cls.M18_X_1_5,
            "1,3/16": cls._1_3_16,
            "1,5/16": cls._1_5_16,
            "1,5/8": cls._1_5_8,
            "1,7/8": cls._1_7_8,
            "2,1/2": cls._2_1_2,
            "5/8": cls._5_8,
            "7/8": cls._7_8,
            "9/16": cls._9_16,
            "5/16": cls._5_16,
            "7/16": cls._7_16,
            "3/4''": cls._3_4_INCH,
        }
        result = mapping.get(value)
        if result is None:
            raise ValueError(f"Thread '{value}' не найден в перечислении")
        return result

class Armature(IntEnum):
    NUT = 1
    UNION = 2
    CONICAL_UNION = 3

class Angle(IntEnum):
    ANGLE_0 = 0
    ANGLE_45 = 45
    ANGLE_90 = 90

class Series(IntEnum):
    LIGHT = 1
    HEAVY = 2
    INTERLOCK = 3