from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Article(BaseModel):
    article: str = Field(..., description="Article number", min_length=1)
    name: str = Field(..., description="Product name", min_length=1)
    description: Optional[str] = Field(None, description="Product description")

    # Technical parameters
    standard: Optional[str] = Field(None, description="Standard: BSP, DKOL, etc.")
    thread: Optional[str] = Field(None, description="Thread size: 1/2, M18x1.5...")
    armature: Optional[str] = Field(None, description="Type: male/female")
    angle: Optional[int] = Field(None, description="Angle: 0, 45, 90", ge=0, le=360)
    dy: Optional[int] = Field(None, description="Nominal diameter Dy in mm", ge=4, le=100)

    # Additional
    series: Optional[str] = Field(None, description="Series: light/heavy")
    component_type: Optional[str] = Field(None, description="fitting/adapter/plug")

    @field_validator("standard")
    @classmethod
    def validate_standard(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.upper().strip()
        return v

    @field_validator("armature")
    @classmethod
    def validate_armature(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        v_lower = v.lower()
        if v_lower in ("male", "папа", "штуцер", "наружная"):
            return "male"
        if v_lower in ("female", "мама", "гайка", "внутренняя"):
            return "female"
        return v_lower

    def to_embedding_text(self) -> str:
        parts = [self.name, self.description or ""]

        if self.standard:
            parts.append(f"Стандарт {self.standard}")
            # Add synonyms
            synonyms = {
                "BSP": "British Standard Pipe цилиндрическая дюймовая",
                "DKOL": "DIN 2353 метрическая лёгкая серия 24 градуса конус",
                "DKOS": "DIN 2353 метрическая тяжёлая серия высокое давление",
                "JIC": "Joint Industry Council 74 градуса авиационная",
                "NPT": "National Pipe Taper коническая американская",
                "ORFS": "O-Ring Face Seal плоское уплотнение",
            }
            if self.standard in synonyms:
                parts.append(synonyms[self.standard])

        if self.thread:
            parts.append(f"Резьба {self.thread}")

        if self.armature:
            parts.append(f"Тип {self.armature}")
            if self.armature == "male":
                parts.extend(["штуцер", "наружная резьба", "папа"])
            else:
                parts.extend(["гайка", "внутренняя резьба", "мама"])

        if self.angle is not None:
            parts.append(f"Угол {self.angle} градусов")
            if self.angle == 90:
                parts.extend(["уголок", "угловой", "прямой угол"])
            elif self.angle == 0:
                parts.extend(["прямой", "прямое соединение"])

        if self.dy:
            parts.append(f"Диаметр Dy {self.dy} мм")

        return ". ".join(filter(None, parts))
