import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from models.file_model import User
from config.db import get_db
from config.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    Token
)
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class UserRegister(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


@router.post("/register", response_model=Token)
async def register(user: UserRegister):
    """Register a new user with email and password"""
    logger.info(f"=== Registration attempt for email: {user.email} ===")
    try:
        with get_db() as db:
            logger.info("Database session opened")
            
            # Check if user already exists
            logger.info(f"Checking if user exists: {user.email}")
            existing_user = db.query(User).filter(User.email == user.email).first()
            if existing_user:
                logger.warning(f"Registration failed: Email already exists - {user.email}")
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
            
            logger.info("User does not exist, proceeding with registration")
            
            # Hash password and create user
            logger.info(f"Hashing password for: {user.email}")
            try:
                hashed_password = hash_password(user.password)
                logger.info(f"Password hashed successfully (hash length: {len(hashed_password)})")
            except Exception as pwd_error:
                logger.error(f"Password hashing failed: {str(pwd_error)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail="Password hashing failed"
                )
            
            logger.info(f"Creating user object for: {user.email}")
            new_user = User(name=user.name, email=user.email, hashed_password=hashed_password)
            
            logger.info("Adding user to database session")
            db.add(new_user)
            logger.info("Committing user to database")
            db.commit()
            logger.info("Refreshing user object from database")
            db.refresh(new_user)
            
            logger.info(f"User created successfully with ID: {new_user.id}")
            
            # Create access token
            logger.info(f"Creating access token for: {new_user.email}")
            access_token = create_access_token(new_user.email)
            logger.info(f"Access token created (length: {len(access_token)})")
            
            logger.info(f"User registered successfully: {user.email}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
    
    except HTTPException:
        logger.warning("HTTPException raised during registration")
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to register user"
        )


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login user with email and password"""
    try:
        logger.info(f"Login attempt for email: {user.email}")
        
        with get_db() as db:
            # Find user by email
            db_user = db.query(User).filter(User.email == user.email).first()
            
            if not db_user:
                logger.warning(f"Login failed: User not found - {user.email}")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )
            
            logger.info(f"User found in database: {user.email}")
            
            # Verify password
            is_password_valid = verify_password(user.password, db_user.hashed_password)
            if not is_password_valid:
                logger.warning(f"Login failed: Invalid password - {user.email}")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )
            
            logger.info(f"Password verified successfully for: {user.email}")
            
            # Create access token
            access_token = create_access_token(db_user.email)
            
            logger.info(f"User logged in successfully: {user.email}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to login user"
        )


@router.post("/verify-token")
async def verify_user_token(token: str):
    """Verify JWT token and return user email"""
    try:
        token_data = verify_token(token)
        
        if not token_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        
        with get_db() as db:
            user = db.query(User).filter(User.email == token_data.email).first()
            
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )
            
            return {
                "email": user.email,
                "id": user.id
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to verify token"
        )
