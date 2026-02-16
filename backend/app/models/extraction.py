
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ExtractionConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ExtractedParams(BaseModel):
    standard: Optional[str] = Field(None, description="Detected standard")
    thread: Optional[str] = Field(None, description="Thread size")
    armature: Optional[str] = Field(None, description="male/female")
    angle: Optional[int] = Field(None, description="Angle in degrees")
    dy: Optional[int] = Field(None, description="Nominal diameter")
    component_type: Optional[str] = Field(None, description="fitting/adapter/plug")
    confidence: ExtractionConfidence = Field(
        ExtractionConfidence.MEDIUM,
        description="Extraction confidence"
    )
    raw_query: Optional[str] = Field(None, description="Original query")

    @field_validator("standard")
    @classmethod
    def normalize_standard(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.upper().strip()
        return v

    @field_validator("armature")
    @classmethod
    def normalize_armature(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        v_lower = v.lower()
        if any(x in v_lower for x in ["male", "пап", "штуц", "наруж"]):
            return "male"
        if any(x in v_lower for x in ["female", "мам", "гайк", "внутр"]):
            return "female"
        return None

    @field_validator("angle")
    @classmethod
    def normalize_angle(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        standard_angles = [0, 45, 90]
        return min(standard_angles, key=lambda x: abs(x - v))

    def has_parameters(self) -> bool:
        return any([
            self.standard,
            self.thread,
            self.armature,
            self.angle is not None,
            self.dy is not None,
            self.component_type,
        ])

    def to_dict(self) -> dict:
        return {
            "standard": self.standard,
            "thread": self.thread,
            "armature": self.armature,
            "angle": self.angle,
            "dy": self.dy,
            "component_type": self.component_type,
            "confidence": self.confidence.value,
        }