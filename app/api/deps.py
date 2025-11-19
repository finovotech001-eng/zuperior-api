from typing import Generator, Optional, Dict
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.database import get_db
from app.core.security import decode_token
from app.models.models import User, RefreshToken
from app.crud.crud import user_crud
from datetime import datetime

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/auth/login")


def get_device_info(request: Request, device_name: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Extract device information from request headers
    
    Args:
        request: FastAPI Request object
        device_name: Optional device name from client
    
    Returns:
        Dictionary with ipAddress, userAgent, and deviceName
    """
    # Get IP address - check X-Forwarded-For first (for proxies/load balancers)
    ip_address = None
    if request.headers.get("X-Forwarded-For"):
        # X-Forwarded-For can contain multiple IPs, take the first one
        ip_address = request.headers.get("X-Forwarded-For").split(",")[0].strip()
    elif request.headers.get("X-Real-IP"):
        ip_address = request.headers.get("X-Real-IP")
    else:
        # Fallback to client host
        if request.client:
            ip_address = request.client.host
    
    # Get user agent
    user_agent = request.headers.get("User-Agent")
    
    # Use provided device name or derive from user agent
    if not device_name and user_agent:
        # Simple device name extraction from user agent
        user_agent_lower = user_agent.lower()
        if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
            device_name = "Mobile Device"
        elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            device_name = "Tablet"
        else:
            device_name = "Desktop"
    
    return {
        "ipAddress": ip_address,
        "userAgent": user_agent,
        "deviceName": device_name
    }


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get current user from JWT token
    Also checks if user has at least one valid refresh token.
    This ensures that if all tokens are revoked via "logout all devices",
    the access token is also invalidated immediately.
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
    
    # Check if user has at least one valid (non-revoked, non-expired) refresh token
    # This ensures that if all tokens are revoked via "logout all devices",
    # the access token is also invalidated immediately
    now = datetime.utcnow()
    valid_token_count = db.query(RefreshToken).filter(
        RefreshToken.userId == user.id,
        RefreshToken.revoked != True,  # Handles None values
        RefreshToken.expiresAt > now
    ).count()
    
    if valid_token_count == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
        RefreshToken.revoked != True,  # Handles None values
        RefreshToken.expiresAt > datetime.utcnow()
    ).first()
    
    if not refresh_token:
        return None
    
    # Update lastActivity timestamp
    refresh_token.lastActivity = datetime.utcnow()
    db.commit()
    
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

