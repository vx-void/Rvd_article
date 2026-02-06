from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Message:
    """
    Универсальное сообщение,
    передаваемое через брокер.
    """
    task_id: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "payload": self.payload,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Message":
        return Message(
            task_id=data["task_id"],
            payload=data.get("payload", {})
        )
