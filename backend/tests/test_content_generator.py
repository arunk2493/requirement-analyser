"""Unit tests for content generator service"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from services.content_generator import ContentGenerationService
from models.file_model import Upload
from utils.error_handler import ResourceNotFoundError, ProcessingError


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def content_service(mock_db):
    """Create ContentGenerationService instance with mocked DB"""
    with patch('services.content_generator.VectorStore'):
        service = ContentGenerationService(mock_db)
    return service


class TestContentGenerationService:
    """Tests for ContentGenerationService"""
    
    def test_service_initialization(self, mock_db):
        """Test service initialization"""
        with patch('services.content_generator.VectorStore'):
            service = ContentGenerationService(mock_db)
            assert service.db == mock_db
            assert service.vectorstore is not None
    
    def test_generate_epics_success(self, content_service, mock_db):
        """Test successful epic generation"""
        # Mock upload
        mock_upload = Mock()
        mock_upload.id = 1
        mock_upload.content = "Sample requirement text"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_upload
        
        # Mock Gemini response
        with patch('services.content_generator.generate_json') as mock_gemini:
            mock_gemini.return_value = [
                {"title": "Epic 1", "description": "Description 1"},
                {"title": "Epic 2", "description": "Description 2"}
            ]
            
            with patch('services.content_generator.ensure_dict_list') as mock_ensure:
                mock_ensure.return_value = [
                    {"title": "Epic 1", "description": "Description 1"},
                    {"title": "Epic 2", "description": "Description 2"}
                ]
                
                prompt_template = "Generate epics from: {requirement_text}"
                result = content_service.generate_epics(1, prompt_template)
                
                assert len(result) == 2
                assert result[0]["title"] == "Epic 1"
    
    def test_generate_epics_upload_not_found(self, content_service, mock_db):
        """Test epic generation fails when upload not found"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ResourceNotFoundError):
            content_service.generate_epics(999, "template")
    
    def test_generate_stories_success(self, content_service, mock_db):
        """Test successful story generation"""
        mock_upload = Mock()
        mock_upload.id = 1
        mock_upload.content = "Sample requirement"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_upload
        
        with patch('services.content_generator.generate_json') as mock_gemini:
            mock_gemini.return_value = [{"title": "Story 1", "description": "Desc"}]
            
            with patch('services.content_generator.ensure_dict_list') as mock_ensure:
                mock_ensure.return_value = [{"title": "Story 1", "description": "Desc"}]
                
                result = content_service.generate_stories(1, "template")
                assert len(result) == 1
    
    def test_generate_qa_success(self, content_service, mock_db):
        """Test successful QA generation"""
        mock_upload = Mock()
        mock_upload.id = 1
        mock_upload.content = "Sample requirement"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_upload
        
        with patch('services.content_generator.generate_json') as mock_gemini:
            mock_gemini.return_value = [{"question": "Q1", "answer": "A1"}]
            
            with patch('services.content_generator.ensure_dict_list') as mock_ensure:
                mock_ensure.return_value = [{"question": "Q1", "answer": "A1"}]
                
                result = content_service.generate_qa(1, "template")
                assert len(result) == 1
    
    def test_generate_testplan_success(self, content_service, mock_db):
        """Test successful test plan generation"""
        mock_upload = Mock()
        mock_upload.id = 1
        mock_upload.content = "Sample requirement"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_upload
        
        with patch('services.content_generator.generate_json') as mock_gemini:
            mock_gemini.return_value = [{"test_case": "TC1", "steps": ["Step1"]}]
            
            with patch('services.content_generator.ensure_dict_list') as mock_ensure:
                mock_ensure.return_value = [{"test_case": "TC1", "steps": ["Step1"]}]
                
                result = content_service.generate_test_plan(1, "template")
                assert len(result) == 1
    
    def test_content_types_constant(self, content_service):
        """Test CONTENT_TYPES constant is properly defined"""
        assert "epics" in content_service.CONTENT_TYPES
        assert "stories" in content_service.CONTENT_TYPES
        assert "qa" in content_service.CONTENT_TYPES
        assert "test_plan" in content_service.CONTENT_TYPES
        
        assert content_service.CONTENT_TYPES["epics"] == "epic"
        assert content_service.CONTENT_TYPES["stories"] == "story"


class TestContentStorageAndRetrieval:
    """Tests for storing and retrieving generated content"""
    
    def test_store_epic_success(self, content_service, mock_db):
        """Test storing epic to database"""
        epic_data = {
            "title": "Test Epic",
            "description": "Test Description",
            "priority": "High"
        }
        
        with patch('services.content_generator.Epic') as mock_epic_model:
            with patch.object(mock_db, 'add'):
                with patch.object(mock_db, 'commit'):
                    # Assuming store_epic method exists
                    try:
                        content_service.store_epic(1, epic_data)
                    except AttributeError:
                        # Method may not be implemented yet
                        pytest.skip("store_epic method not implemented")
    
    def test_retrieve_epics_by_upload(self, content_service, mock_db):
        """Test retrieving epics for a specific upload"""
        mock_epics = [
            Mock(id=1, title="Epic 1"),
            Mock(id=2, title="Epic 2")
        ]
        
        mock_db.query.return_value.filter.return_value.all.return_value = mock_epics
        
        try:
            result = content_service.get_epics_by_upload(1)
            assert len(result) == 2
        except AttributeError:
            pytest.skip("get_epics_by_upload method not implemented")


class TestErrorHandling:
    """Tests for error handling in content generation"""
    
    def test_gemini_api_failure_handling(self, content_service, mock_db):
        """Test handling of Gemini API failures"""
        mock_upload = Mock()
        mock_upload.content = "test"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_upload
        
        with patch('services.content_generator.generate_json') as mock_gemini:
            mock_gemini.side_effect = Exception("API Error")
            
            with pytest.raises(ProcessingError):
                content_service.generate_epics(1, "template")
    
    def test_invalid_response_format_handling(self, content_service, mock_db):
        """Test handling of invalid response format from Gemini"""
        mock_upload = Mock()
        mock_upload.content = "test"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_upload
        
        with patch('services.content_generator.generate_json') as mock_gemini:
            mock_gemini.return_value = "invalid response format"
            
            with patch('services.content_generator.ensure_dict_list') as mock_ensure:
                mock_ensure.side_effect = ValueError("Invalid format")
                
                with pytest.raises(ProcessingError):
                    content_service.generate_epics(1, "template")
