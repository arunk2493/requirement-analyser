"""Unit tests for database models"""

import pytest
from datetime import datetime
from models.file_model import User, Upload, Epic, Story, QA, AggregatedUpload
from config.db import Base


class TestUserModel:
    """Test User model"""
    
    def test_user_instantiation(self):
        """Test creating a User instance"""
        user = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            hashed_password="hashed_pwd_123"
        )
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.hashed_password == "hashed_pwd_123"
    
    def test_user_with_jira_credentials(self):
        """Test User with Jira credentials"""
        user = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            hashed_password="hashed_pwd",
            jira_url="https://jira.company.com",
            jira_username="john",
            jira_api_token="token_123",
            jira_project_key="PROJ"
        )
        assert user.jira_url == "https://jira.company.com"
        assert user.jira_username == "john"
        assert user.jira_api_token == "token_123"
        assert user.jira_project_key == "PROJ"
    
    def test_user_optional_fields(self):
        """Test User with optional fields as None"""
        user = User(
            id=1,
            name="John",
            email="john@example.com",
            hashed_password="pwd"
        )
        assert user.jira_url is None
        assert user.jira_username is None
        assert user.jira_api_token is None
        assert user.jira_project_key is None
    
    def test_user_tablename(self):
        """Test User tablename"""
        assert User.__tablename__ == "users"


class TestUploadModel:
    """Test Upload model"""
    
    def test_upload_instantiation(self):
        """Test creating an Upload instance"""
        upload = Upload(
            id=1,
            user_id=1,
            filename="requirements.pdf",
            content={"text": "Some content"}
        )
        assert upload.id == 1
        assert upload.user_id == 1
        assert upload.filename == "requirements.pdf"
        assert upload.content == {"text": "Some content"}
    
    def test_upload_with_vectorstore_id(self):
        """Test Upload with vectorstore_id"""
        upload = Upload(
            id=1,
            user_id=1,
            filename="requirements.pdf",
            content={"text": "content"},
            vectorstore_id="vs_123"
        )
        assert upload.vectorstore_id == "vs_123"
    
    def test_upload_with_confluence_page_id(self):
        """Test Upload with confluence_page_id"""
        upload = Upload(
            id=1,
            user_id=1,
            filename="doc.pdf",
            content={},
            confluence_page_id="page_456"
        )
        assert upload.confluence_page_id == "page_456"
    
    def test_upload_tablename(self):
        """Test Upload tablename"""
        assert Upload.__tablename__ == "uploads"


class TestEpicModel:
    """Test Epic model"""
    
    def test_epic_instantiation(self):
        """Test creating an Epic instance"""
        epic = Epic(
            id=1,
            upload_id=1,
            name="User Authentication",
            content={"description": "Authentication system"}
        )
        assert epic.id == 1
        assert epic.upload_id == 1
        assert epic.name == "User Authentication"
        assert epic.content == {"description": "Authentication system"}
    
    def test_epic_with_jira_details(self):
        """Test Epic with Jira integration details"""
        epic = Epic(
            id=1,
            upload_id=1,
            name="Feature X",
            content={},
            jira_key="PROJ-1",
            jira_issue_id="10028",
            jira_url="https://jira.company.com/browse/PROJ-1",
            jira_creation_success=True
        )
        assert epic.jira_key == "PROJ-1"
        assert epic.jira_issue_id == "10028"
        assert epic.jira_url == "https://jira.company.com/browse/PROJ-1"
        assert epic.jira_creation_success is True
    
    def test_epic_jira_creation_failed(self):
        """Test Epic with failed Jira creation"""
        epic = Epic(
            id=1,
            upload_id=1,
            name="Feature",
            content={},
            jira_creation_success=False
        )
        assert epic.jira_creation_success is False
    
    def test_epic_jira_creation_not_attempted(self):
        """Test Epic with Jira creation not attempted"""
        epic = Epic(
            id=1,
            upload_id=1,
            name="Feature",
            content={},
            jira_creation_success=None
        )
        assert epic.jira_creation_success is None
    
    def test_epic_with_confluence_page_id(self):
        """Test Epic with Confluence page ID"""
        epic = Epic(
            id=1,
            upload_id=1,
            name="Epic 1",
            content={},
            confluence_page_id="conf_123"
        )
        assert epic.confluence_page_id == "conf_123"
    
    def test_epic_tablename(self):
        """Test Epic tablename"""
        assert Epic.__tablename__ == "epics"


class TestStoryModel:
    """Test Story model"""
    
    def test_story_instantiation(self):
        """Test creating a Story instance"""
        story = Story(
            id=1,
            epic_id=1,
            name="Login as User",
            content={"acceptance_criteria": "User can login"}
        )
        assert story.id == 1
        assert story.epic_id == 1
        assert story.name == "Login as User"
        assert story.content == {"acceptance_criteria": "User can login"}
    
    def test_story_with_jira_details(self):
        """Test Story with Jira details"""
        story = Story(
            id=1,
            epic_id=1,
            name="Login Story",
            content={},
            jira_key="PROJ-2",
            jira_issue_id="10030",
            jira_url="https://jira.company.com/browse/PROJ-2",
            epic_jira_key="PROJ-1",
            epic_jira_issue_id="10028",
            jira_creation_success=True
        )
        assert story.jira_key == "PROJ-2"
        assert story.jira_issue_id == "10030"
        assert story.epic_jira_key == "PROJ-1"
        assert story.epic_jira_issue_id == "10028"
    
    def test_story_jira_creation_failed(self):
        """Test Story with failed Jira creation"""
        story = Story(
            id=1,
            epic_id=1,
            name="Story",
            content={},
            jira_creation_success=False
        )
        assert story.jira_creation_success is False
    
    def test_story_tablename(self):
        """Test Story tablename"""
        assert Story.__tablename__ == "stories"


class TestQAModel:
    """Test QA model"""
    
    def test_qa_instantiation_with_story_id(self):
        """Test creating QA instance linked to story"""
        qa = QA(
            id=1,
            story_id=1,
            type="test_plan",
            content={"test_cases": []}
        )
        assert qa.id == 1
        assert qa.story_id == 1
        assert qa.type == "test_plan"
        assert qa.content == {"test_cases": []}
    
    def test_qa_instantiation_with_epic_id(self):
        """Test creating QA instance linked to epic"""
        qa = QA(
            id=1,
            epic_id=1,
            type="api_test",
            content={}
        )
        assert qa.epic_id == 1
        assert qa.type == "api_test"
    
    def test_qa_with_test_type(self):
        """Test QA with test_type"""
        qa = QA(
            id=1,
            story_id=1,
            type="test_plan",
            test_type="functional",
            content={}
        )
        assert qa.test_type == "functional"
    
    def test_qa_types(self):
        """Test QA with different types"""
        types = ["test_plan", "api_test", "automation_script"]
        for qa_type in types:
            qa = QA(
                id=1,
                story_id=1,
                type=qa_type,
                content={}
            )
            assert qa.type == qa_type
    
    def test_qa_test_types(self):
        """Test QA with different test_types"""
        test_types = ["functional", "non_functional", "api"]
        for test_type in test_types:
            qa = QA(
                id=1,
                story_id=1,
                type="test_plan",
                test_type=test_type,
                content={}
            )
            assert qa.test_type == test_type
    
    def test_qa_with_confluence_page_id(self):
        """Test QA with Confluence page ID"""
        qa = QA(
            id=1,
            story_id=1,
            type="test_plan",
            content={},
            confluence_page_id="conf_qa_123"
        )
        assert qa.confluence_page_id == "conf_qa_123"
    
    def test_qa_tablename(self):
        """Test QA tablename"""
        assert QA.__tablename__ == "qa"


class TestAggregatedUploadModel:
    """Test AggregatedUpload model"""
    
    def test_aggregated_upload_instantiation(self):
        """Test creating AggregatedUpload instance"""
        aggregated = AggregatedUpload(
            id=1,
            upload_id=1,
            content={"hierarchy": "full structure"}
        )
        assert aggregated.id == 1
        assert aggregated.upload_id == 1
        assert aggregated.content == {"hierarchy": "full structure"}
    
    def test_aggregated_upload_complex_content(self):
        """Test AggregatedUpload with complex nested content"""
        content = {
            "epics": [
                {
                    "name": "Epic 1",
                    "stories": [
                        {"name": "Story 1", "qa": []}
                    ]
                }
            ]
        }
        aggregated = AggregatedUpload(
            id=1,
            upload_id=1,
            content=content
        )
        assert aggregated.content == content
        assert len(aggregated.content["epics"]) == 1
    
    def test_aggregated_upload_tablename(self):
        """Test AggregatedUpload tablename"""
        assert AggregatedUpload.__tablename__ == "aggregated_uploads"


class TestModelInheritance:
    """Test that all models inherit from Base"""
    
    def test_user_inherits_from_base(self):
        """Test User inherits from Base"""
        assert hasattr(User, '__tablename__')
        assert hasattr(User, 'id')
    
    def test_upload_inherits_from_base(self):
        """Test Upload inherits from Base"""
        assert hasattr(Upload, '__tablename__')
        assert hasattr(Upload, 'id')
    
    def test_epic_inherits_from_base(self):
        """Test Epic inherits from Base"""
        assert hasattr(Epic, '__tablename__')
        assert hasattr(Epic, 'id')
    
    def test_story_inherits_from_base(self):
        """Test Story inherits from Base"""
        assert hasattr(Story, '__tablename__')
        assert hasattr(Story, 'id')
    
    def test_qa_inherits_from_base(self):
        """Test QA inherits from Base"""
        assert hasattr(QA, '__tablename__')
        assert hasattr(QA, 'id')
    
    def test_aggregated_upload_inherits_from_base(self):
        """Test AggregatedUpload inherits from Base"""
        assert hasattr(AggregatedUpload, '__tablename__')
        assert hasattr(AggregatedUpload, 'id')


class TestUserModelAdvanced:
    """Advanced tests for User model"""
    
    def test_user_with_all_fields(self):
        """Test User with all fields populated"""
        user = User(
            id=1,
            name="Complete User",
            email="user@example.com",
            hashed_password="hashed_123",
            jira_url="https://jira.example.com",
            jira_username="user123",
            jira_api_token="token_xyz",
            jira_project_key="PROJ"
        )
        
        assert user.id == 1
        assert user.name == "Complete User"
        assert user.email == "user@example.com"
        assert user.hashed_password == "hashed_123"
        assert user.jira_url == "https://jira.example.com"
        assert user.jira_username == "user123"
        assert user.jira_api_token == "token_xyz"
        assert user.jira_project_key == "PROJ"
    
    def test_user_email_validation(self):
        """Test User with various email formats"""
        emails = [
            "simple@example.com",
            "user+tag@example.co.uk",
            "first.last@example.com"
        ]
        
        for email in emails:
            user = User(
                id=1,
                name="User",
                email=email,
                hashed_password="pwd"
            )
            assert user.email == email
    
    def test_user_long_jira_url(self):
        """Test User with very long Jira URL"""
        long_url = "https://jira.company.example.com:8080/jira/secure/browse/PROJ-1234567890"
        user = User(
            id=1,
            name="User",
            email="user@example.com",
            hashed_password="pwd",
            jira_url=long_url
        )
        
        assert user.jira_url == long_url
    
    def test_user_empty_name(self):
        """Test User with empty name"""
        user = User(
            id=1,
            name="",
            email="user@example.com",
            hashed_password="pwd"
        )
        
        assert user.name == ""
    
    def test_user_special_characters_in_name(self):
        """Test User with special characters in name"""
        user = User(
            id=1,
            name="José María O'Brien-Smith",
            email="user@example.com",
            hashed_password="pwd"
        )
        
        assert user.name == "José María O'Brien-Smith"


class TestUploadModelAdvanced:
    """Advanced tests for Upload model"""
    
    def test_upload_with_complex_content(self):
        """Test Upload with complex nested content"""
        content = {
            "text": "Some text",
            "metadata": {
                "author": "John",
                "tags": ["tag1", "tag2"],
                "nested": {"key": "value"}
            }
        }
        
        upload = Upload(
            id=1,
            user_id=1,
            filename="complex.pdf",
            content=content
        )
        
        assert upload.content == content
        assert upload.content["metadata"]["nested"]["key"] == "value"
    
    def test_upload_with_empty_content(self):
        """Test Upload with empty content"""
        upload = Upload(
            id=1,
            user_id=1,
            filename="empty.txt",
            content={}
        )
        
        assert upload.content == {}
    
    def test_upload_with_large_content(self):
        """Test Upload with large content"""
        large_content = {
            "text": "x" * 100000,
            "metadata": {"size": "large"}
        }
        
        upload = Upload(
            id=1,
            user_id=1,
            filename="large.pdf",
            content=large_content
        )
        
        assert len(upload.content["text"]) == 100000
    
    def test_upload_filename_with_special_chars(self):
        """Test Upload with special characters in filename"""
        filenames = [
            "document-2025-01-12.pdf",
            "file (1).txt",
            "report_final_v3.xlsx",
            "日本語ファイル.pdf"
        ]
        
        for filename in filenames:
            upload = Upload(
                id=1,
                user_id=1,
                filename=filename,
                content={}
            )
            
            assert upload.filename == filename


class TestEpicModelAdvanced:
    """Advanced tests for Epic model"""
    
    def test_epic_all_jira_fields_present(self):
        """Test Epic with all Jira fields"""
        epic = Epic(
            id=1,
            upload_id=1,
            name="Complete Epic",
            content={"description": "test"},
            jira_key="PROJ-1",
            jira_issue_id="10001",
            jira_url="https://jira.example.com/browse/PROJ-1",
            confluence_page_id="123456",
            jira_creation_success=True
        )
        
        assert epic.jira_key == "PROJ-1"
        assert epic.jira_issue_id == "10001"
        assert epic.jira_url == "https://jira.example.com/browse/PROJ-1"
        assert epic.confluence_page_id == "123456"
        assert epic.jira_creation_success is True
    
    def test_epic_with_numeric_issue_id(self):
        """Test Epic with various numeric issue IDs"""
        for issue_id in ["1", "10000", "999999"]:
            epic = Epic(
                id=1,
                upload_id=1,
                name="Epic",
                content={},
                jira_issue_id=issue_id
            )
            assert epic.jira_issue_id == issue_id
    
    def test_epic_jira_key_formats(self):
        """Test Epic with different Jira key formats"""
        keys = ["PROJ-1", "AB-100", "TEST-9999", "A-1"]
        
        for key in keys:
            epic = Epic(
                id=1,
                upload_id=1,
                name="Epic",
                content={},
                jira_key=key
            )
            assert epic.jira_key == key


class TestStoryModelAdvanced:
    """Advanced tests for Story model"""
    
    def test_story_with_parent_epic_tracking(self):
        """Test Story with parent epic tracking"""
        story = Story(
            id=1,
            epic_id=1,
            name="Story",
            content={},
            epic_jira_key="PROJ-1",
            epic_jira_issue_id="10001"
        )
        
        assert story.epic_id == 1
        assert story.epic_jira_key == "PROJ-1"
        assert story.epic_jira_issue_id == "10001"
    
    def test_story_full_hierarchy(self):
        """Test Story with complete hierarchy info"""
        story = Story(
            id=5,
            epic_id=2,
            name="Complete Story",
            content={"description": "test"},
            jira_key="PROJ-3",
            jira_issue_id="10003",
            jira_url="https://jira.example.com/browse/PROJ-3",
            epic_jira_key="PROJ-1",
            epic_jira_issue_id="10001",
            jira_creation_success=True
        )
        
        assert story.epic_id == 2
        assert story.jira_key == "PROJ-3"
        assert story.epic_jira_key == "PROJ-1"


class TestQAModelAdvanced:
    """Advanced tests for QA model"""
    
    def test_qa_linked_to_story_and_epic(self):
        """Test QA linked to both story and epic"""
        qa = QA(
            id=1,
            story_id=1,
            epic_id=2,
            type="test_plan",
            test_type="functional",
            content={"test_cases": []}
        )
        
        assert qa.story_id == 1
        assert qa.epic_id == 2
    
    def test_qa_only_story_link(self):
        """Test QA linked only to story (epic can be None)"""
        qa = QA(
            id=1,
            story_id=5,
            epic_id=None,
            type="automation_script",
            content={}
        )
        
        assert qa.story_id == 5
        assert qa.epic_id is None
    
    def test_qa_only_epic_link(self):
        """Test QA linked only to epic (story can be None)"""
        qa = QA(
            id=1,
            story_id=None,
            epic_id=2,
            type="api_test",
            content={}
        )
        
        assert qa.story_id is None
        assert qa.epic_id == 2
    
    def test_qa_all_type_combinations(self):
        """Test QA with all valid type combinations"""
        qa_types = ["test_plan", "api_test", "automation_script"]
        test_types = ["functional", "non_functional", "api", None]
        
        for qa_type in qa_types:
            for test_type in test_types:
                qa = QA(
                    id=1,
                    story_id=1,
                    type=qa_type,
                    test_type=test_type,
                    content={}
                )
                
                assert qa.type == qa_type
                assert qa.test_type == test_type
    
    def test_qa_with_large_content(self):
        """Test QA with large content"""
        large_content = {
            "test_cases": [
                {"id": i, "description": f"Test case {i}"} 
                for i in range(1000)
            ]
        }
        
        qa = QA(
            id=1,
            story_id=1,
            type="test_plan",
            content=large_content
        )
        
        assert len(qa.content["test_cases"]) == 1000


class TestAggregatedUploadModelAdvanced:
    """Advanced tests for AggregatedUpload model"""
    
    def test_aggregated_upload_full_hierarchy(self):
        """Test AggregatedUpload with complete hierarchy"""
        content = {
            "epics": [
                {
                    "id": 1,
                    "name": "Epic 1",
                    "stories": [
                        {"id": 1, "name": "Story 1"},
                        {"id": 2, "name": "Story 2"}
                    ],
                    "qa": [
                        {"id": 1, "type": "test_plan"}
                    ]
                },
                {
                    "id": 2,
                    "name": "Epic 2",
                    "stories": [
                        {"id": 3, "name": "Story 3"}
                    ]
                }
            ]
        }
        
        agg = AggregatedUpload(
            id=1,
            upload_id=1,
            content=content
        )
        
        assert len(agg.content["epics"]) == 2
        assert agg.content["epics"][0]["id"] == 1
    
    def test_aggregated_upload_empty_hierarchy(self):
        """Test AggregatedUpload with empty hierarchy"""
        agg = AggregatedUpload(
            id=1,
            upload_id=1,
            content={"epics": []}
        )
        
        assert agg.content["epics"] == []


class TestModelFieldTypes:
    """Test various field types across models"""
    
    def test_user_integer_fields(self):
        """Test User with integer fields"""
        user = User(
            id=999999,
            name="User",
            email="user@example.com",
            hashed_password="pwd"
        )
        
        assert isinstance(user.id, int)
        assert user.id == 999999
    
    def test_upload_integer_fields(self):
        """Test Upload with integer fields"""
        upload = Upload(
            id=777,
            user_id=888,
            filename="test.txt",
            content={}
        )
        
        assert isinstance(upload.id, int)
        assert isinstance(upload.user_id, int)
    
    def test_epic_string_fields(self):
        """Test Epic with various string fields"""
        epic = Epic(
            id=1,
            upload_id=1,
            name="String test epic",
            content={},
            jira_key="ABC-123",
            jira_issue_id="5000",
            jira_url="https://example.com"
        )
        
        assert isinstance(epic.name, str)
        assert isinstance(epic.jira_key, str)


class TestModelRelationships:
    """Test relationships between models"""
    
    def test_upload_belongs_to_user(self):
        """Test that Upload references User via user_id"""
        upload = Upload(
            id=1,
            user_id=10,
            filename="test.pdf",
            content={}
        )
        
        assert upload.user_id == 10
    
    def test_epic_belongs_to_upload(self):
        """Test that Epic references Upload via upload_id"""
        epic = Epic(
            id=1,
            upload_id=5,
            name="Epic",
            content={}
        )
        
        assert epic.upload_id == 5
    
    def test_story_belongs_to_epic(self):
        """Test that Story references Epic via epic_id"""
        story = Story(
            id=1,
            epic_id=3,
            name="Story",
            content={}
        )
        
        assert story.epic_id == 3
    
    def test_qa_can_reference_story_or_epic(self):
        """Test that QA can reference either Story or Epic"""
        qa_with_story = QA(
            id=1,
            story_id=7,
            epic_id=None,
            type="test_plan",
            content={}
        )
        
        qa_with_epic = QA(
            id=2,
            story_id=None,
            epic_id=4,
            type="test_plan",
            content={}
        )
        
        assert qa_with_story.story_id == 7
        assert qa_with_epic.epic_id == 4
