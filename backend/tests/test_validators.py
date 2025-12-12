"""Unit tests for validators utility"""
import pytest
from datetime import datetime
from pydantic import ValidationError as PydanticValidationError
from utils.validators import (
    PaginationParams,
    SortParams,
    BaseResponse,
    ErrorResponse,
    validate_request_body
)


class TestPaginationParams:
    """Tests for PaginationParams model"""
    
    def test_default_pagination_params(self):
        """Test default pagination values"""
        params = PaginationParams()
        assert params.skip == 0
        assert params.limit == 10
    
    def test_custom_pagination_params(self):
        """Test custom pagination values"""
        params = PaginationParams(skip=20, limit=50)
        assert params.skip == 20
        assert params.limit == 50
    
    def test_pagination_validation_skip_negative(self):
        """Test that negative skip is rejected"""
        with pytest.raises(PydanticValidationError):
            PaginationParams(skip=-1, limit=10)
    
    def test_pagination_validation_limit_zero(self):
        """Test that zero limit is rejected"""
        with pytest.raises(PydanticValidationError):
            PaginationParams(skip=0, limit=0)
    
    def test_pagination_validation_limit_exceeds_max(self):
        """Test that limit exceeding max (100) is rejected"""
        with pytest.raises(PydanticValidationError):
            PaginationParams(skip=0, limit=101)
    
    def test_pagination_valid_boundary_values(self):
        """Test valid boundary values"""
        params = PaginationParams(skip=0, limit=100)
        assert params.skip == 0
        assert params.limit == 100


class TestSortParams:
    """Tests for SortParams model"""
    
    def test_default_sort_params(self):
        """Test default sort values"""
        params = SortParams()
        assert params.sort_by == "created_at"
        assert params.order == "desc"
    
    def test_custom_sort_params(self):
        """Test custom sort values"""
        params = SortParams(sort_by="name", order="asc")
        assert params.sort_by == "name"
        assert params.order == "asc"
    
    def test_sort_order_validation_valid_asc(self):
        """Test valid ascending sort order"""
        params = SortParams(order="asc")
        assert params.order == "asc"
    
    def test_sort_order_validation_valid_desc(self):
        """Test valid descending sort order"""
        params = SortParams(order="desc")
        assert params.order == "desc"
    
    def test_sort_order_validation_invalid(self):
        """Test that invalid sort order is rejected"""
        with pytest.raises(PydanticValidationError):
            SortParams(order="invalid")
    
    def test_sort_field_names(self):
        """Test various sort field names"""
        for field in ["id", "name", "created_at", "updated_at", "priority"]:
            params = SortParams(sort_by=field)
            assert params.sort_by == field


class TestBaseResponse:
    """Tests for BaseResponse model"""
    
    def test_success_response(self):
        """Test successful response"""
        response = BaseResponse(
            success=True,
            message="Operation completed",
            data={"id": 1, "name": "test"}
        )
        assert response.success is True
        assert response.message == "Operation completed"
        assert response.data["id"] == 1
        assert response.error is None
    
    def test_error_response(self):
        """Test error response"""
        response = BaseResponse(
            success=False,
            message="Operation failed",
            error="Invalid input"
        )
        assert response.success is False
        assert response.error == "Invalid input"
        assert response.data is None
    
    def test_response_timestamp(self):
        """Test response includes timestamp"""
        before = datetime.now()
        response = BaseResponse(success=True, message="test")
        after = datetime.now()
        
        assert before <= response.timestamp <= after
    
    def test_response_with_complex_data(self):
        """Test response with nested data"""
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ],
            "meta": {"count": 2}
        }
        response = BaseResponse(success=True, message="Users fetched", data=complex_data)
        assert len(response.data["users"]) == 2
        assert response.data["meta"]["count"] == 2


class TestErrorResponse:
    """Tests for ErrorResponse model"""
    
    def test_error_response_minimal(self):
        """Test minimal error response"""
        response = ErrorResponse(detail="Something went wrong")
        assert response.detail == "Something went wrong"
        assert response.error_code is None
    
    def test_error_response_with_code(self):
        """Test error response with error code"""
        response = ErrorResponse(
            detail="Validation failed",
            error_code="VALIDATION_ERROR"
        )
        assert response.detail == "Validation failed"
        assert response.error_code == "VALIDATION_ERROR"
    
    def test_error_response_timestamp(self):
        """Test error response includes timestamp"""
        response = ErrorResponse(detail="Error occurred")
        assert isinstance(response.timestamp, datetime)
    
    def test_error_response_various_codes(self):
        """Test error response with different error codes"""
        for code in ["NOT_FOUND", "INVALID_INPUT", "SERVER_ERROR", "UNAUTHORIZED"]:
            response = ErrorResponse(detail="Error", error_code=code)
            assert response.error_code == code


class TestValidateRequestBody:
    """Tests for validate_request_body function"""
    
    def test_valid_request_body(self):
        """Test validation of valid request body"""
        data = {"name": "John", "email": "john@example.com"}
        required_fields = ["name", "email"]
        # Should not raise exception
        validate_request_body(data, required_fields)
    
    def test_missing_required_field(self):
        """Test validation fails when required field is missing"""
        data = {"name": "John"}
        required_fields = ["name", "email"]
        with pytest.raises(ValueError):
            validate_request_body(data, required_fields)
    
    def test_all_required_fields_present(self):
        """Test validation with all required fields present"""
        data = {"name": "Jane", "email": "jane@example.com", "age": 30}
        required_fields = ["name", "email"]
        # Should not raise exception
        validate_request_body(data, required_fields)
    
    def test_extra_fields_allowed(self):
        """Test that extra fields beyond required are allowed"""
        data = {"name": "Bob", "email": "bob@example.com", "extra": "field"}
        required_fields = ["name", "email"]
        # Should not raise exception
        validate_request_body(data, required_fields)
    
    def test_empty_required_fields_list(self):
        """Test validation with empty required fields list"""
        data = {"anything": "goes"}
        required_fields = []
        # Should not raise exception
        validate_request_body(data, required_fields)
    
    def test_empty_data_with_required_fields(self):
        """Test validation fails with empty data and required fields"""
        data = {}
        required_fields = ["required_field"]
        with pytest.raises(ValueError):
            validate_request_body(data, required_fields)
    
    def test_field_with_none_value(self):
        """Test that None values fail validation"""
        data = {"name": None, "email": "test@example.com"}
        required_fields = ["name", "email"]
        with pytest.raises(ValueError):
            validate_request_body(data, required_fields)
    
    def test_field_with_empty_string(self):
        """Test that empty string is allowed (not validated by default)"""
        data = {"name": "", "email": "test@example.com"}
        required_fields = ["name", "email"]
        # Empty strings are allowed by validate_request_body (it only checks for None)
        validate_request_body(data, required_fields)
