from fastapi import HTTPException, status

class HydroSearchException(Exception):
    pass

class LLMError(HydroSearchException):
    pass

class LLMIndexError(HydroSearchException):
    pass

class ValidationError(HydroSearchException):
    pass