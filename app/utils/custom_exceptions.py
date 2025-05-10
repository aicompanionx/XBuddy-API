from fastapi import HTTPException, status
from typing import Any, Optional


class ApiException(HTTPException):
    """
    API exception base class
    """
    def __init__(
        self, 
        status_code: int,
        code: int,
        message: str,
        data: Optional[Any] = None,
    ):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(status_code=status_code, detail=message)


class BadRequestException(ApiException):
    """400 error: bad request"""
    def __init__(self, message: str = "bad request", data: Any = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=400,
            message=message,
            data=data
        )


class UnauthorizedException(ApiException):
    """401 error: unauthorized access"""
    def __init__(self, message: str = "unauthorized access", data: Any = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=401,
            message=message,
            data=data
        )


class ForbiddenException(ApiException):
    """403 error: forbidden access"""
    def __init__(self, message: str = "forbidden access", data: Any = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code=403,
            message=message,
            data=data
        )


class NotFoundException(ApiException):
    """404 error: resource not found"""
    def __init__(self, message: str = "resource not found", data: Any = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code=404,
            message=message,
            data=data
        )


class ServerException(ApiException):
    """500 error: internal server error"""
    def __init__(self, message: str = "internal server error", data: Any = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=500,
            message=message,
            data=data
        ) 
        
class ExternalApiException(ApiException):
    """503 error: external API service unavailable"""
    def __init__(self, message: str = "external API service unavailable", data: Any = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code=503,
            message=message,
            data=data
        )
