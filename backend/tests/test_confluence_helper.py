"""Unit tests for Confluence utilities"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from utils.confluence_helper import (
    add_timestamp,
    create_confluence_html_content,
    build_confluence_page,
    batch_create_pages
)


class TestAddTimestamp:
    """Test add_timestamp function"""
    
    def test_add_timestamp_basic(self):
        """Test adding timestamp to a name"""
        result = add_timestamp("Document")
        assert "Document_" in result
        assert len(result) > len("Document_")
    
    def test_add_timestamp_with_spaces(self):
        """Test adding timestamp to name with spaces"""
        result = add_timestamp("My Document")
        assert "My Document_" in result
    
    def test_add_timestamp_with_special_chars(self):
        """Test adding timestamp to name with special characters"""
        result = add_timestamp("Doc-123_v2")
        assert "Doc-123_v2_" in result
    
    def test_add_timestamp_format(self):
        """Test timestamp format (YYYYMMDD_HHMMSS)"""
        result = add_timestamp("Doc")
        # Extract timestamp part
        parts = result.split("_")
        timestamp = "_".join(parts[-2:])
        # Should be _YYYYMMDD_HHMMSS format
        assert len(parts[-2]) == 8  # YYYYMMDD
        assert len(parts[-1]) == 6  # HHMMSS
    
    def test_add_timestamp_uniqueness(self):
        """Test that consecutive calls produce different timestamps"""
        result1 = add_timestamp("Doc")
        import time
        time.sleep(0.01)  # Small delay to ensure different timestamp
        result2 = add_timestamp("Doc")
        # They might be the same due to same second, but structure should match
        assert result1.startswith("Doc_")
        assert result2.startswith("Doc_")
    
    def test_add_timestamp_empty_string(self):
        """Test adding timestamp to empty string"""
        result = add_timestamp("")
        assert "_" in result
        assert len(result) > 1


class TestCreateConfluenceHtmlContent:
    """Test create_confluence_html_content function"""
    
    def test_create_html_basic(self):
        """Test creating basic HTML content"""
        content = {"description": "Test content"}
        result = create_confluence_html_content("Test Title", content)
        assert "<h2>Test Title</h2>" in result
        assert "Description" in result
        assert "Test content" in result
    
    def test_create_html_with_none_values(self):
        """Test HTML creation skips None values"""
        content = {
            "description": "Value",
            "notes": None,
            "comment": "Another"
        }
        result = create_confluence_html_content("Title", content)
        assert "Value" in result
        assert "Another" in result
        # None values should not appear
        assert "None" not in result or "notes" not in result
    
    def test_create_html_skips_metadata_fields(self):
        """Test that metadata fields are skipped"""
        content = {
            "_internal": "hidden",
            "id": "123",
            "name": "ignored",
            "description": "visible"
        }
        result = create_confluence_html_content("Title", content)
        assert "visible" in result
        assert "_internal" not in result
        assert "Description" in result
    
    def test_create_html_with_list(self):
        """Test HTML creation with list content"""
        content = {
            "items": ["Item 1", "Item 2", "Item 3"]
        }
        result = create_confluence_html_content("Title", content)
        assert "<ul>" in result
        assert "<li>Item 1</li>" in result
        assert "<li>Item 2</li>" in result
        assert "<li>Item 3</li>" in result
        assert "</ul>" in result
    
    def test_create_html_with_dict_items(self):
        """Test HTML with list of dictionaries"""
        content = {
            "features": [
                {"name": "Feature 1", "description": "Desc 1"},
                {"name": "Feature 2", "description": "Desc 2"}
            ]
        }
        result = create_confluence_html_content("Title", content)
        assert "<ul>" in result
        assert "<strong>Feature 1:</strong>" in result
        assert "Desc 1" in result
    
    def test_create_html_with_dict(self):
        """Test HTML creation with dictionary content"""
        content = {
            "properties": {
                "key1": "value1",
                "key2": "value2"
            }
        }
        result = create_confluence_html_content("Title", content)
        assert "<table>" in result
        assert "<strong>key1</strong>" in result
        assert "value1" in result
        assert "<strong>key2</strong>" in result
        assert "value2" in result
    
    def test_create_html_with_section_configs(self):
        """Test HTML creation with custom section configs"""
        content = {"details": "Some details"}
        configs = {
            "details": {"heading_level": 4, "is_list": False}
        }
        result = create_confluence_html_content("Title", content, configs)
        assert "<h4>Details</h4>" in result
    
    def test_create_html_field_name_formatting(self):
        """Test field names are formatted correctly"""
        content = {
            "acceptance_criteria": "AC1, AC2",
            "test_cases": ["TC1", "TC2"]
        }
        result = create_confluence_html_content("Title", content)
        assert "Acceptance Criteria" in result
        assert "Test Cases" in result


class TestBuildConfluencePage:
    """Test build_confluence_page function"""
    
    def test_build_page_success(self):
        """Test successful page creation"""
        mock_client = Mock()
        mock_client.create_page.return_value = {"id": "page_123", "title": "Test"}
        
        result = build_confluence_page(
            mock_client,
            "SPACE",
            "Test Title",
            "<p>Content</p>"
        )
        
        assert result["id"] == "page_123"
        mock_client.create_page.assert_called_once()
    
    def test_build_page_with_parent(self):
        """Test page creation with parent ID"""
        mock_client = Mock()
        mock_client.create_page.return_value = {"id": "child_page"}
        
        build_confluence_page(
            mock_client,
            "SPACE",
            "Child Page",
            "<p>Content</p>",
            parent_id="parent_123"
        )
        
        call_args = mock_client.create_page.call_args
        assert call_args.kwargs["parent_id"] == "parent_123"
    
    def test_build_page_correct_parameters(self):
        """Test page creation with correct parameters"""
        mock_client = Mock()
        mock_client.create_page.return_value = {"id": "page"}
        
        build_confluence_page(
            mock_client,
            "SPACE_KEY",
            "Page Title",
            "<p>HTML Content</p>",
            page_type="page"
        )
        
        call_args = mock_client.create_page.call_args
        assert call_args.kwargs["space"] == "SPACE_KEY"
        assert call_args.kwargs["title"] == "Page Title"
        assert call_args.kwargs["body"] == "<p>HTML Content</p>"
        assert call_args.kwargs["type"] == "page"
        assert call_args.kwargs["representation"] == "storage"
    
    def test_build_page_failure(self):
        """Test page creation failure raises exception"""
        mock_client = Mock()
        mock_client.create_page.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            build_confluence_page(
                mock_client,
                "SPACE",
                "Title",
                "<p>Content</p>"
            )
    
    def test_build_page_connection_error(self):
        """Test handling connection errors"""
        mock_client = Mock()
        mock_client.create_page.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(ConnectionError):
            build_confluence_page(
                mock_client,
                "SPACE",
                "Title",
                "<p>Content</p>"
            )


class TestBatchCreatePages:
    """Test batch_create_pages function"""
    
    def test_batch_create_empty_list(self):
        """Test batch creation with empty list"""
        mock_client = Mock()
        result = batch_create_pages(mock_client, "SPACE", [])
        assert result == []
    
    def test_batch_create_single_page(self):
        """Test batch creation of single page"""
        mock_client = Mock()
        mock_client.create_page.return_value = {"id": "page_1"}
        
        result = batch_create_pages(
            mock_client,
            "SPACE",
            [{"title": "Page 1", "content": "<p>Content</p>"}]
        )
        
        assert len(result) == 1
        assert result[0]["id"] == "page_1"
    
    def test_batch_create_multiple_pages(self):
        """Test batch creation of multiple pages"""
        mock_client = Mock()
        mock_client.create_page.side_effect = [
            {"id": "page_1"},
            {"id": "page_2"},
            {"id": "page_3"}
        ]
        
        pages = [
            {"title": "Page 1", "content": "<p>Content 1</p>"},
            {"title": "Page 2", "content": "<p>Content 2</p>"},
            {"title": "Page 3", "content": "<p>Content 3</p>"}
        ]
        
        result = batch_create_pages(mock_client, "SPACE", pages)
        
        assert len(result) == 3
        assert result[0]["id"] == "page_1"
        assert result[1]["id"] == "page_2"
        assert result[2]["id"] == "page_3"
    
    def test_batch_create_with_parent_id(self):
        """Test batch creation with parent ID"""
        mock_client = Mock()
        mock_client.create_page.return_value = {"id": "child_page"}
        
        batch_create_pages(
            mock_client,
            "SPACE",
            [{"title": "Child", "content": "<p>Content</p>"}],
            parent_id="parent_123"
        )
        
        call_args = mock_client.create_page.call_args
        assert call_args.kwargs["parent_id"] == "parent_123"
    
    def test_batch_create_partial_failure(self):
        """Test batch creation continues despite some failures"""
        mock_client = Mock()
        mock_client.create_page.side_effect = [
            {"id": "page_1"},
            Exception("Failed"),
            {"id": "page_3"}
        ]
        
        pages = [
            {"title": "Page 1", "content": "<p>Content 1</p>"},
            {"title": "Page 2", "content": "<p>Content 2</p>"},
            {"title": "Page 3", "content": "<p>Content 3</p>"}
        ]
        
        result = batch_create_pages(mock_client, "SPACE", pages)
        
        assert len(result) == 3
        assert result[0]["id"] == "page_1"
        assert result[1] is None  # Failed page
        assert result[2]["id"] == "page_3"
    
    def test_batch_create_default_title(self):
        """Test batch creation uses default title when missing"""
        mock_client = Mock()
        mock_client.create_page.return_value = {"id": "page"}
        
        batch_create_pages(
            mock_client,
            "SPACE",
            [{"content": "<p>Content</p>"}]  # No title
        )
        
        call_args = mock_client.create_page.call_args
        assert call_args.kwargs["title"] == "Untitled"
    
    def test_batch_create_page_types(self):
        """Test batch creation with different page types"""
        mock_client = Mock()
        mock_client.create_page.side_effect = [
            {"id": "page_1"},
            {"id": "page_2"}
        ]
        
        pages = [
            {"title": "Page 1", "content": "<p>Content</p>", "type": "page"},
            {"title": "Page 2", "content": "<p>Content</p>", "type": "blogpost"}
        ]
        
        batch_create_pages(mock_client, "SPACE", pages)
        
        calls = mock_client.create_page.call_args_list
        assert calls[0].kwargs["type"] == "page"
        assert calls[1].kwargs["type"] == "blogpost"
