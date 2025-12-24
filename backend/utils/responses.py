# backend/utils/responses.py
from flask import jsonify
from typing import Any, Optional
from datetime import datetime


class APIResponse:
    """Базовый класс для всех API ответов"""

    def __init__(self, success: bool, request_id: Optional[str] = None):
        self.success = success
        self.timestamp = datetime.now().isoformat()
        self.request_id = request_id

    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        result = {
            "success": self.success,
            "timestamp": self.timestamp,
        }
        if self.request_id:
            result["request_id"] = self.request_id
        return result

    def to_response(self, status_code: int = 200):
        """Создание Flask Response"""
        return jsonify(self.to_dict()), status_code


class SuccessResponse(APIResponse):

    def __init__(self, data: Any = None, request_id: Optional[str] = None):
        super().__init__(success=True, request_id=request_id)
        self.data = data

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.data is not None:
            result["data"] = self.data
        return result


class ErrorResponse(APIResponse):
    def __init__(self,
                 message: str,
                 status_code: int = 400,
                 request_id: Optional[str] = None,
                 details: Optional[dict] = None):
        super().__init__(success=False, request_id=request_id)
        self.message = message
        self.status_code = status_code
        self.details = details

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["error"] = {
            "message": self.message,
            "details": self.details
        }
        return result

    def to_response(self):
        """Переопределение с учетом status_code"""
        return jsonify(self.to_dict()), self.status_code


# Функции для обратной совместимости
def success_response(data=None, request_id=None):
    """Создание успешного ответа (старый стиль)"""
    response = SuccessResponse(data, request_id)
    return response.to_response()


def error_response(message, status_code=400, request_id=None, details=None):
    """Создание ответа с ошибкой (старый стиль)"""
    response = ErrorResponse(message, status_code, request_id, details)
    return response.to_response()