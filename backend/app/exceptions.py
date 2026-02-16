"""Custom exceptions for the application."""

from fastapi import HTTPException, status


class HydroSearchException(Exception):
    pass


class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Invalid or missing API key"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

class RateLimitExceeded(HTTPException):
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": "60"},
        )


class LLMError(HydroSearchException):
    pass

class LLMIndexError(HydroSearchException):
    pass

class ValidationError(HydroSearchException):
    pass