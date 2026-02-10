#parser.py

from typing import Optional


class AIResponseParser:

    @staticmethod
    def normalize_classification(text: str, allowed: set[str]) -> Optional[str]:
        text = text.lower().strip()
        return text if text in allowed else None

    @staticmethod
    def extract_quantity(text: str) -> Optional[int]:
        digits = "".join(filter(str.isdigit, text))
        return int(digits) if digits else None
