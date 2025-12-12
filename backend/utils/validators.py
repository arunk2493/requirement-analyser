"""Request and response validation utilities"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class PaginationParams(BaseModel):
    """Common pagination parameters"""
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(10, ge=1, le=100, description="Number of items to return")


class SortParams(BaseModel):
    """Common sorting parameters"""
    sort_by: str = Field("created_at", description="Field to sort by")
    order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ValidationRequest(BaseModel):
    """Generic validation request"""
    data: Dict[str, Any]
    rules: Optional[Dict[str, Any]] = None


def validate_request_body(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate request body has required fields.
    
    Args:
        data: Request data
        required_fields: List of required field names
        
    Raises:
        ValueError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")


def sanitize_input(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
        
    Raises:
        ValueError: If input exceeds max length
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")
    
    if len(value) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length}")
    
    # Strip whitespace
    return value.strip()


def validate_pagination(skip: int, limit: int) -> tuple:
    """
    Validate and normalize pagination parameters.
    
    Args:
        skip: Skip count
        limit: Limit count
        
    Returns:
        Tuple of (skip, limit)
        
    Raises:
        ValueError: If parameters are invalid
    """
    if skip < 0:
        raise ValueError("skip must be >= 0")
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")
    
    return skip, limit
