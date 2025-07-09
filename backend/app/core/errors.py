from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

class AppError(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class AppErrorException(HTTPException):
    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.code = code
        self.error_message = message
        self.details = details
        super().__init__(status_code=status_code, detail=self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.error_message,
                "details": self.details
            }
        }

class DatabaseError(AppErrorException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="DATABASE_ERROR",
            message=message,
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class ValidationError(AppErrorException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            details=details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

class AuthenticationError(AppErrorException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="AUTHENTICATION_ERROR",
            message=message,
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class PermissionError(AppErrorException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="PERMISSION_ERROR",
            message=message,
            details=details,
            status_code=status.HTTP_403_FORBIDDEN
        )

class NotFoundError(AppErrorException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="NOT_FOUND",
            message=message,
            details=details,
            status_code=status.HTTP_404_NOT_FOUND
        )
