"""Unit tests for error handler utility"""
import pytest
from fastapi import status
from utils.error_handler import (
    APIError,
    ValidationError,
    ResourceNotFoundError,
    ProcessingError
)


class TestAPIError:
    """Tests for APIError base exception"""
    
    def test_create_api_error(self):
        """Test creating basic APIError"""
        error = APIError("Test error message", status_code=400)
        assert error.message == "Test error message"
        assert error.status_code == 400
    
    def test_api_error_with_detail(self):
        """Test APIError with detail dictionary"""
        detail = {"field": "email", "issue": "invalid format"}
        error = APIError("Validation failed", status_code=400, detail=detail)
        assert error.detail == detail
    
    def test_api_error_default_status_code(self):
        """Test APIError uses 500 as default status code"""
        error = APIError("Server error")
        assert error.status_code == 500


class TestValidationError:
    """Tests for ValidationError exception"""
    
    def test_validation_error_creation(self):
        """Test creating ValidationError"""
        error = ValidationError("Invalid input")
        assert error.message == "Invalid input"
        assert error.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_validation_error_with_detail(self):
        """Test ValidationError with details"""
        detail = {"field": "username", "reason": "too short"}
        error = ValidationError("Username validation failed", detail=detail)
        assert error.detail == detail
        assert error.status_code == 400
    
    def test_validation_error_inheritance(self):
        """Test ValidationError is subclass of APIError"""
        assert issubclass(ValidationError, APIError)


class TestResourceNotFoundError:
    """Tests for ResourceNotFoundError exception"""
    
    def test_resource_not_found_error(self):
        """Test creating ResourceNotFoundError"""
        error = ResourceNotFoundError("Upload", 123)
        assert "Upload" in error.message
        assert "123" in error.message
        assert error.status_code == status.HTTP_404_NOT_FOUND
    
    def test_resource_not_found_detail(self):
        """Test ResourceNotFoundError includes detail"""
        error = ResourceNotFoundError("User", 456)
        assert error.detail["resource_type"] == "User"
        assert error.detail["resource_id"] == 456
    
    def test_different_resource_types(self):
        """Test with different resource types"""
        for resource_type in ["Upload", "User", "Epic", "Story"]:
            error = ResourceNotFoundError(resource_type, 999)
            assert resource_type in error.message


class TestProcessingError:
    """Tests for ProcessingError exception"""
    
    def test_processing_error_creation(self):
        """Test creating ProcessingError"""
        error = ProcessingError("Generation failed")
        assert error.message == "Generation failed"
        assert error.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_processing_error_with_operation(self):
        """Test ProcessingError with operation name"""
        error = ProcessingError("Failed to generate", operation="epic_generation")
        assert error.detail["operation"] == "epic_generation"
    
    def test_processing_error_with_custom_detail(self):
        """Test ProcessingError with custom detail"""
        detail = {"error_code": "GEMINI_API_ERROR", "retries": 3}
        error = ProcessingError("API failed", detail=detail)
        assert error.detail == detail
    
    def test_processing_error_status_code(self):
        """Test ProcessingError uses 500 status code"""
        error = ProcessingError("Processing failed")
        assert error.status_code == 500


class TestErrorInheritance:
    """Tests for error class inheritance"""
    
    def test_all_errors_inherit_from_api_error(self):
        """Test that all custom errors inherit from APIError"""
        errors = [
            ValidationError("test"),
            ResourceNotFoundError("Type", 1),
            ProcessingError("test")
        ]
        for error in errors:
            assert isinstance(error, APIError)
    
    def test_all_errors_are_exceptions(self):
        """Test that all errors are proper Exception subclasses"""
        errors = [
            APIError("test"),
            ValidationError("test"),
            ResourceNotFoundError("Type", 1),
            ProcessingError("test")
        ]
        for error in errors:
            assert isinstance(error, Exception)
