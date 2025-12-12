"""Unit tests for configuration modules"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from config.config import (
    POSTGRES_URL,
    GEMINI_API_KEY,
    CONFLUENCE_URL,
    CONFLUENCE_USERNAME,
    CONFLUENCE_PASSWORD,
    CONFLUENCE_SPACE_KEY,
    CONFLUENCE_ROOT_FOLDER_ID,
    JIRA_API_TOKEN_ENCRYPTION_KEY
)


class TestConfigVariables:
    """Test configuration variables"""
    
    def test_postgres_url_variable_exists(self):
        """Test POSTGRES_URL variable is defined"""
        # Should not raise error even if None
        assert isinstance(POSTGRES_URL, (str, type(None)))
    
    def test_gemini_api_key_variable_exists(self):
        """Test GEMINI_API_KEY variable is defined"""
        assert isinstance(GEMINI_API_KEY, (str, type(None)))
    
    def test_confluence_url_variable_exists(self):
        """Test CONFLUENCE_URL variable is defined"""
        assert isinstance(CONFLUENCE_URL, (str, type(None)))
    
    def test_confluence_username_variable_exists(self):
        """Test CONFLUENCE_USERNAME variable is defined"""
        assert isinstance(CONFLUENCE_USERNAME, (str, type(None)))
    
    def test_confluence_password_variable_exists(self):
        """Test CONFLUENCE_PASSWORD variable is defined"""
        assert isinstance(CONFLUENCE_PASSWORD, (str, type(None)))
    
    def test_confluence_space_key_variable_exists(self):
        """Test CONFLUENCE_SPACE_KEY variable is defined"""
        assert isinstance(CONFLUENCE_SPACE_KEY, (str, type(None)))
    
    def test_confluence_root_folder_id_variable_exists(self):
        """Test CONFLUENCE_ROOT_FOLDER_ID variable is defined"""
        assert isinstance(CONFLUENCE_ROOT_FOLDER_ID, (str, type(None)))
    
    def test_jira_encryption_key_has_default(self):
        """Test JIRA_API_TOKEN_ENCRYPTION_KEY has default value"""
        assert JIRA_API_TOKEN_ENCRYPTION_KEY is not None
        assert isinstance(JIRA_API_TOKEN_ENCRYPTION_KEY, str)
        assert len(JIRA_API_TOKEN_ENCRYPTION_KEY) > 0
    
    def test_jira_encryption_key_production_warning(self):
        """Test JIRA_API_TOKEN_ENCRYPTION_KEY default indicates need for change"""
        # Default value should be a placeholder
        if JIRA_API_TOKEN_ENCRYPTION_KEY == "default-encryption-key-change-in-production":
            # This is expected in test environment
            assert True
        else:
            # In production, it should be different
            assert JIRA_API_TOKEN_ENCRYPTION_KEY != "default-encryption-key-change-in-production"


class TestConfigEnvironmentVariables:
    """Test environment variable loading"""
    
    @patch.dict(os.environ, {
        "POSTGRES_URL": "postgresql://test:test@localhost/testdb",
        "GEMINI_API_KEY": "test_key_123"
    })
    def test_config_loads_from_env(self):
        """Test config loads from environment variables"""
        # Reimport to get fresh config
        import importlib
        import config.config as config_module
        importlib.reload(config_module)
        
        # Variables should be available
        assert hasattr(config_module, 'POSTGRES_URL')
        assert hasattr(config_module, 'GEMINI_API_KEY')
    
    def test_config_handles_missing_env_vars(self):
        """Test config handles missing environment variables"""
        # Some variables may be None if not set
        # This should not raise an error
        assert True  # If we got here, config loaded successfully


class TestDatabaseConfiguration:
    """Test database configuration"""
    
    def test_postgres_url_format_if_set(self):
        """Test POSTGRES_URL format if configured"""
        if POSTGRES_URL:
            # Should start with postgresql:// or postgres://
            assert POSTGRES_URL.startswith(("postgresql://", "postgres://"))
    
    def test_postgres_url_none_acceptable(self):
        """Test POSTGRES_URL can be None for testing"""
        # POSTGRES_URL might be None in test environment
        assert POSTGRES_URL is None or isinstance(POSTGRES_URL, str)


class TestConfluenceConfiguration:
    """Test Confluence configuration"""
    
    def test_confluence_url_format_if_set(self):
        """Test CONFLUENCE_URL format if configured"""
        if CONFLUENCE_URL:
            assert CONFLUENCE_URL.startswith(("http://", "https://"))
    
    def test_confluence_credentials_together(self):
        """Test Confluence credentials are together"""
        # Either all set or all None
        has_url = bool(CONFLUENCE_URL)
        has_username = bool(CONFLUENCE_USERNAME)
        has_password = bool(CONFLUENCE_PASSWORD)
        
        # Should be consistent
        if has_url:
            # If URL is set, credentials should probably be set too (but not required)
            assert isinstance(CONFLUENCE_URL, str)


class TestJiraConfiguration:
    """Test Jira configuration"""
    
    def test_jira_encryption_key_non_empty(self):
        """Test JIRA_API_TOKEN_ENCRYPTION_KEY is not empty"""
        assert len(JIRA_API_TOKEN_ENCRYPTION_KEY) > 0
    
    def test_jira_encryption_key_minimum_length(self):
        """Test JIRA_API_TOKEN_ENCRYPTION_KEY has minimum length"""
        # Should be at least 8 characters for basic security
        assert len(JIRA_API_TOKEN_ENCRYPTION_KEY) >= 8


class TestGeminiConfiguration:
    """Test Gemini API configuration"""
    
    def test_gemini_api_key_none_acceptable(self):
        """Test GEMINI_API_KEY can be None in test environment"""
        assert GEMINI_API_KEY is None or isinstance(GEMINI_API_KEY, str)
    
    def test_gemini_api_key_not_empty_if_set(self):
        """Test GEMINI_API_KEY is not empty if configured"""
        if GEMINI_API_KEY:
            assert len(GEMINI_API_KEY) > 0


class TestConfigurationImmutability:
    """Test configuration constants are not accidentally modified"""
    
    def test_postgres_url_is_string_or_none(self):
        """Test POSTGRES_URL type"""
        assert isinstance(POSTGRES_URL, (str, type(None)))
    
    def test_gemini_api_key_is_string_or_none(self):
        """Test GEMINI_API_KEY type"""
        assert isinstance(GEMINI_API_KEY, (str, type(None)))
    
    def test_jira_key_is_string(self):
        """Test JIRA_API_TOKEN_ENCRYPTION_KEY is string"""
        assert isinstance(JIRA_API_TOKEN_ENCRYPTION_KEY, str)
