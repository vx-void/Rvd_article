from datetime import datetime
from typing import Any, Dict, Optional
from flask import jsonify


class APIResponse:
    """
    Базовая модель HTTP-ответа.
    """

    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        request_id: Optional[str] = None,
        status_code: int = 200
    ) -> None:
        self.success = success
        self.data = data or {}
        self.error = error
        self.request_id = request_id
        self.status_code = status_code
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "timestamp": self.timestamp,
            "request_id": self.request_id,
            "data": self.data if self.success else None,
            "error": self.error if not self.success else None
        }

    def to_response(self):
        return jsonify(self.to_dict()), self.status_code


class SuccessResponse(APIResponse):
    def __init__(
        self,
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        status_code: int = 200
    ) -> None:
        super().__init__(
            success=True,
            data=data,
            request_id=request_id,
            status_code=status_code
        )


class ErrorResponse(APIResponse):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        request_id: Optional[str] = None
    ) -> None:
        super().__init__(
            success=False,
            error=message,
            request_id=request_id,
            status_code=status_code
        )
