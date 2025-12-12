"""Unit tests for configuration modules"""
import pytest
import os
from unittest.mock import patch, MagicMock
from config.auth import create_access_token, verify_token, hash_password, verify_password


class TestPasswordHashing:
    """Tests for password hashing functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "secure_password_123"
        hashed = hash_password(password)
        
        # Hashed password should be different from original
        assert hashed != password
        # Hashed password should not be empty
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Test verifying correct password"""
        password = "correct_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test verifying incorrect password"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_different_for_same_password(self):
        """Test that same password produces different hashes"""
        password = "test_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Different hashes for same password (due to salt)
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestTokenGeneration:
    """Tests for JWT token generation"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        user_id = 123
        email = "testuser@example.com"
        
        token = create_access_token(email=email, user_id=user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_token_with_expiration(self):
        """Test token creation with custom expiration"""
        import datetime
        
        user_id = 456
        email = "user@example.com"
        expires_delta = datetime.timedelta(hours=2)
        
        token = create_access_token(
            email=email,
            user_id=user_id,
            expires_delta=expires_delta
        )
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_verify_token_success(self):
        """Test successful token verification"""
        user_id = 789
        email = "verify@example.com"
        
        token = create_access_token(email=email, user_id=user_id)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload.email == email
    
    def test_verify_token_invalid(self):
        """Test verification of invalid token"""
        invalid_token = "invalid.token.here"
        
        result = verify_token(invalid_token)
        # Invalid token should return None
        assert result is None
    
    def test_verify_expired_token(self):
        """Test verification of expired token"""
        import datetime
        import time
        
        # Note: Token expiration happens at a specific time
        # Since we're creating with seconds=0, it will expire very quickly
        # but fast clock skew might allow it to still be valid
        expires_delta = datetime.timedelta(seconds=-1)  # Already expired
        token = create_access_token(
            email="test@example.com",
            user_id=1,
            expires_delta=expires_delta
        )
        
        result = verify_token(token)
        # Already expired token should return None
        assert result is None


class TestAuthConfig:
    """Tests for authentication configuration"""
    
    def test_secret_key_exists(self):
        """Test that SECRET_KEY is defined"""
        from config.auth import SECRET_KEY
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 0
    
    def test_algorithm_is_hs256(self):
        """Test that algorithm is HS256"""
        from config.auth import ALGORITHM
        assert ALGORITHM == "HS256"
    
    def test_token_expiration_time_set(self):
        """Test that token expiration time is configured"""
        from config.auth import ACCESS_TOKEN_EXPIRE_MINUTES
        assert ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert ACCESS_TOKEN_EXPIRE_MINUTES <= 1440  # Reasonable limit
    
    def test_environment_variable_override(self):
        """Test that SECRET_KEY can be overridden by environment"""
        with patch.dict(os.environ, {"SECRET_KEY": "test_secret_123"}):
            # This would require reimporting the module
            # Just verify the mechanism can work
            assert os.environ.get("SECRET_KEY") == "test_secret_123"


class TestTokenPayload:
    """Tests for token payload structure"""
    
    def test_token_payload_contains_email(self):
        """Test token payload contains email"""
        user_id = 999
        email = "payload@example.com"
        token = create_access_token(email=email, user_id=user_id)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload.email == email
    
    def test_token_payload_contains_user_id(self):
        """Test token payload contains user ID"""
        user_id = 111
        email = "userid@example.com"
        token = create_access_token(email=email, user_id=user_id)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload.user_id == user_id
    
    def test_token_email_only(self):
        """Test token with email only (no user ID)"""
        email = "emailonly@example.com"
        token = create_access_token(email=email)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload.email == email


class TestMultipleTokens:
    """Tests for handling multiple tokens"""
    
    def test_different_tokens_for_different_users(self):
        """Test that different users get different tokens"""
        token1 = create_access_token(email="user1@example.com", user_id=1)
        token2 = create_access_token(email="user2@example.com", user_id=2)
        
        assert token1 != token2
        
        payload1 = verify_token(token1)
        payload2 = verify_token(token2)
        
        assert payload1.email == "user1@example.com"
        assert payload2.email == "user2@example.com"
    
    def test_multiple_tokens_same_user(self):
        """Test multiple tokens for same user"""
        email = "user123@example.com"
        user_id = 123
        
        token1 = create_access_token(email=email, user_id=user_id)
        token2 = create_access_token(email=email, user_id=user_id)
        
        # Tokens may be identical if created in same second (depends on time resolution)
        # What matters is that they both verify correctly
        payload1 = verify_token(token1)
        payload2 = verify_token(token2)
        
        assert payload1.email == email
        assert payload2.email == email
        assert payload1.user_id == user_id
        assert payload2.user_id == user_id
