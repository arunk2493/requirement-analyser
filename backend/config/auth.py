import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Password hashing - using simple approach that doesn't depend on bcrypt
try:
    from passlib.context import CryptContext
    # Try pbkdf2 which is always available in passlib
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    logger.info("Password hashing initialized with pbkdf2_sha256")
except Exception as e:
    logger.error(f"Failed to initialize password hashing: {str(e)}")
    # Fallback: use simple hash if passlib fails completely
    pwd_context = None

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
security = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    email: str
    user_id: Optional[int] = None


class Token(BaseModel):
    access_token: str
    token_type: str


def hash_password(password: str) -> str:
    """Hash a password using pbkdf2_sha256"""
    try:
        if not pwd_context:
            raise RuntimeError("Password context not initialized")
        
        # Ensure password is not too long
        password = password[:72]
        
        hashed = pwd_context.hash(password)
        logger.info("Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}", exc_info=True)
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        if not pwd_context:
            logger.error("Password context not initialized")
            return False
        
        # Ensure password is not too long
        plain_password = plain_password[:72]
        
        is_valid = pwd_context.verify(plain_password, hashed_password)
        return is_valid
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}", exc_info=True)
        return False


def create_access_token(email: str, user_id: int = None, expires_delta: timedelta = None) -> str:
    """Create a JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"email": email, "exp": expire}
    if user_id:
        to_encode["user_id"] = user_id
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        user_id: int = payload.get("user_id")
        
        if email is None:
            logger.warning("Token verification failed: Missing email claim in JWT")
            return None
        
        logger.debug(f"Token verified: email={email}, user_id={user_id}")
        return TokenData(email=email, user_id=user_id)
    except JWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {str(e)}", exc_info=True)
        return None


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> TokenData:
    """Dependency function to validate JWT token from Authorization header"""
    import logging
    logger = logging.getLogger(__name__)
    
    if not credentials:
        logger.warning("Authentication failed: Missing authentication credentials (no Authorization header)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Missing authentication credentials. Please include Authorization header with Bearer token",
                "status": "unauthorized",
                "code": "MISSING_BEARER_TOKEN",
                "help": "Include Authorization header with Bearer token: Authorization: Bearer {your_jwt_token}",
                "steps": [
                    "1. Call POST /auth/register or POST /auth/login to get access_token",
                    "2. Include header: Authorization: Bearer {access_token}",
                    "3. Retry the request"
                ]
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    logger.debug(f"Received token: {token[:20]}..." if len(token) > 20 else f"Received token: {token}")
    
    token_data = verify_token(token)
    
    if not token_data:
        logger.warning("Authentication failed: Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Invalid or expired token. Please login again",
                "status": "unauthorized",
                "code": "INVALID_TOKEN",
                "help": "Get a new token by calling POST /auth/login with your credentials",
                "steps": [
                    "1. Call POST /auth/login with email and password",
                    "2. Use the new access_token in Authorization header",
                    "3. Retry the request"
                ]
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Authentication successful: user_email={token_data.email}, user_id={token_data.user_id}")
    return token_data
