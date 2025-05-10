from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ErrorCode:
    """Error code definition"""
    SUCCESS = 0
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    VALIDATION_ERROR = 422
    SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


async def validation_exception_handler(request, exc: RequestValidationError):
    """
    Handle request validation error
    """
    errors = []
    for error in exc.errors():
        error_loc = " -> ".join([str(loc) for loc in error["loc"]])
        errors.append(f"{error_loc}: {error['msg']}")

    error_msg = f"Request validation failed: {', '.join(errors)}"
    logger.warning(f"Request validation error: {request.url.path} - {error_msg}")
    
    return JSONResponse(
        status_code=400,
        content={"code": 400, "msg": error_msg},
    )


async def http_exception_handler(request, exc: StarletteHTTPException):
    """
    Handle HTTP exception
    """
    logger.warning(f"HTTP exception: {request.url.path} - status code: {exc.status_code}, message: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "msg": exc.detail},
    )


async def pydantic_validation_handler(request, exc: ValidationError):
    """
    Handle Pydantic validation error
    """
    errors = []
    for error in exc.errors():
        error_loc = " -> ".join([str(loc) for loc in error["loc"]])
        errors.append(f"{error_loc}: {error['msg']}")

    error_msg = f"Data validation failed: {', '.join(errors)}"
    logger.warning(f"Data validation error: {request.url.path} - {error_msg}")
    
    return JSONResponse(
        status_code=400,
        content={"code": 400, "msg": error_msg},
    )


async def general_exception_handler(request, exc: Exception):
    """
    Handle general exception
    """
    # Get error details and stack trace
    error_detail = str(exc)
    stack_trace = traceback.format_exc()
    
    # Log error
    logger.error(f"Unhandled exception: {request.url.path} - {error_detail}\n{stack_trace}")
    
    # For security reasons, do not return detailed stack trace to client in production environment
    return JSONResponse(
        status_code=500,
        content={"code": 500, "msg": f"Internal server error: {error_detail}"},
    )