from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.auth import verify_token, TokenData
from config.db import get_db
from models.file_model import User

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    Dependency to verify JWT token and return current user's token data.
    Use this in route parameters to protect routes.
    
    Example:
    @router.get("/protected")
    def protected_route(current_user: TokenData = Depends(get_current_user)):
        return {"user_id": current_user.user_id, "email": current_user.email}
    """
    token = credentials.credentials
    token_data = verify_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    with get_db() as db:
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
    
    return token_data

def get_current_user_with_db(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to verify JWT token and return current user object from database.
    Use this when you need access to the full user object.
    """
    token = credentials.credentials
    token_data = verify_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    with get_db() as db:
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
    
    return user
