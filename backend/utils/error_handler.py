"""Error handling utilities with consistent responses"""
import logging
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from functools import wraps

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = 500, detail: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """Raised for validation failures"""
    def __init__(self, message: str, detail: Optional[Dict] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, detail)


class ResourceNotFoundError(APIError):
    """Raised when resource is not found"""
    def __init__(self, resource_type: str, resource_id: Any):
        message = f"{resource_type} with id {resource_id} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND, {"resource_type": resource_type, "resource_id": resource_id})


class ProcessingError(APIError):
    """Raised for processing/generation errors"""
    def __init__(self, message: str, operation: str = "", detail: Optional[Dict] = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, detail or {"operation": operation})


def handle_errors(operation_name: str = "operation"):
    """
    Decorator for consistent error handling in route handlers.
    
    Args:
        operation_name: Name of the operation for logging
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except APIError as e:
                logger.error(f"{operation_name} failed: {e.message}", extra=e.detail)
                raise HTTPException(status_code=e.status_code, detail=e.message)
            except Exception as e:
                logger.exception(f"Unexpected error in {operation_name}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred"
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except APIError as e:
                logger.error(f"{operation_name} failed: {e.message}", extra=e.detail)
                raise HTTPException(status_code=e.status_code, detail=e.message)
            except Exception as e:
                logger.exception(f"Unexpected error in {operation_name}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred"
                )
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_required_fields(data: Dict, required_fields: list) -> None:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Raises:
        ValidationError: If any required field is missing
    """
    missing = [field for field in required_fields if field not in data or data[field] is None]
    if missing:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing)}",
            {"missing_fields": missing}
        )


def wrap_api_response(success: bool, message: str, data: Any = None, error: Optional[str] = None) -> Dict:
    """
    Create a standardized API response format.
    
    Args:
        success: Whether operation succeeded
        message: Human-readable message
        data: Response data
        error: Error details if applicable
        
    Returns:
        Standardized response dictionary
    """
    response = {
        "success": success,
        "message": message,
    }
    if data is not None:
        response["data"] = data
    if error:
        response["error"] = error
    return response
