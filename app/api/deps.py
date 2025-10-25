from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from core.database import get_db
from core.security import decode_token
from models.models import User, RefreshToken
from crud.crud import user_crud
from datetime import datetime

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get current user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")
    
    if user_id is None or token_type != "access":
        raise credentials_exception
    
    user = user_crud.get_by_id(db, id=user_id)
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    """
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def verify_refresh_token(
    db: Session,
    token: str
) -> Optional[User]:
    """
    Verify refresh token and return user
    """
    payload = decode_token(token)
    if payload is None:
        return None
    
    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")
    
    if user_id is None or token_type != "refresh":
        return None
    
    # Check if token exists in database and is not revoked
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == token,
        RefreshToken.userId == user_id,
        RefreshToken.revoked == False,
        RefreshToken.expiresAt > datetime.utcnow()
    ).first()
    
    if not refresh_token:
        return None
    
    user = user_crud.get_by_id(db, id=user_id)
    return user


def require_role(required_role: str):
    """
    Dependency factory for role-based access control
    """
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role} role"
            )
        return current_user
    return role_checker

