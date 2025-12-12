"""Unit tests for JSON parser utility"""
import json
import pytest
from utils.json_parser import extract_valid_json, parse_model_json, ensure_dict_list


class TestExtractValidJson:
    """Tests for extract_valid_json function"""
    
    def test_valid_json_object(self):
        """Test parsing valid JSON object"""
        json_str = '{"name": "John", "age": 30}'
        result = extract_valid_json(json_str)
        assert result == {"name": "John", "age": 30}
    
    def test_valid_json_array(self):
        """Test parsing valid JSON array"""
        json_str = '[1, 2, 3, 4, 5]'
        result = extract_valid_json(json_str)
        assert result == [1, 2, 3, 4, 5]
    
    def test_json_with_code_fence_json(self):
        """Test JSON extraction with ```json fence"""
        json_str = '```json\n{"status": "success"}\n```'
        result = extract_valid_json(json_str)
        assert result == {"status": "success"}
    
    def test_json_with_code_fence_python(self):
        """Test JSON extraction with ```python fence"""
        json_str = '```python\n{"data": [1, 2, 3]}\n```'
        result = extract_valid_json(json_str)
        assert result == {"data": [1, 2, 3]}
    
    def test_json_with_single_quotes(self):
        """Test JSON with single quotes converted to double quotes"""
        json_str = "{'name': 'Alice', 'role': 'admin'}"
        result = extract_valid_json(json_str)
        assert result == {"name": "Alice", "role": "admin"}
    
    def test_json_with_trailing_commas(self):
        """Test JSON with trailing commas removed"""
        json_str = '{"items": [1, 2, 3,], "count": 3,}'
        result = extract_valid_json(json_str)
        assert result == {"items": [1, 2, 3], "count": 3}
    
    def test_json_with_nested_objects(self):
        """Test parsing nested JSON objects"""
        json_str = '{"user": {"id": 1, "name": "Bob", "settings": {"theme": "dark"}}}'
        result = extract_valid_json(json_str)
        assert result["user"]["name"] == "Bob"
        assert result["user"]["settings"]["theme"] == "dark"
    
    def test_json_extraction_from_text(self):
        """Test extracting JSON from mixed text"""
        text = 'Here is the JSON: {"id": 123, "status": "active"} and some more text'
        result = extract_valid_json(text)
        assert result == {"id": 123, "status": "active"}
    
    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError"""
        with pytest.raises(ValueError):
            extract_valid_json("This is not JSON at all")
    
    def test_empty_string_raises_error(self):
        """Test that empty string raises ValueError"""
        with pytest.raises(ValueError):
            extract_valid_json("")
    
    def test_non_string_input_raises_error(self):
        """Test that non-string input raises ValueError"""
        with pytest.raises(ValueError):
            extract_valid_json(123)
        
        with pytest.raises(ValueError):
            extract_valid_json(None)
    
    def test_whitespace_handling(self):
        """Test JSON parsing with extra whitespace"""
        json_str = '  \n  {"key": "value"}  \n  '
        result = extract_valid_json(json_str)
        assert result == {"key": "value"}


class TestParseModelJson:
    """Tests for parse_model_json function"""
    
    def test_parse_valid_epic_json(self):
        """Test parsing valid epic JSON"""
        json_str = '{"title": "Epic 1", "description": "Description", "priority": "High"}'
        result = parse_model_json(json_str)
        assert result["title"] == "Epic 1"
        assert result["description"] == "Description"
    
    def test_parse_epic_with_code_fence(self):
        """Test parsing epic with code fence"""
        json_str = '```json\n{"title": "Epic", "description": "Desc", "priority": "Medium"}\n```'
        result = parse_model_json(json_str)
        assert "title" in result
    
    def test_parse_invalid_json_raises_error(self):
        """Test that invalid JSON raises error"""
        with pytest.raises(ValueError):
            parse_model_json("Invalid JSON")


class TestEnsureDictList:
    """Tests for ensure_dict_list function"""
    
    def test_list_of_dicts(self):
        """Test that list of dicts is returned as-is"""
        data = [{"id": 1}, {"id": 2}]
        result = ensure_dict_list(data)
        assert result == data
        assert len(result) == 2
    
    def test_single_dict_converted_to_list(self):
        """Test that single dict is converted to list"""
        data = {"id": 1, "name": "item"}
        result = ensure_dict_list(data)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == data
    
    def test_empty_list(self):
        """Test empty list returns empty list"""
        result = ensure_dict_list([])
        assert result == []
    
    def test_nested_structure(self):
        """Test list with nested objects"""
        data = [
            {"id": 1, "items": [{"sub_id": 1}]},
            {"id": 2, "items": [{"sub_id": 2}]}
        ]
        result = ensure_dict_list(data)
        assert len(result) == 2
        assert result[0]["items"][0]["sub_id"] == 1
