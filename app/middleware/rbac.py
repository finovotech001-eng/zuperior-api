"""
Role-Based Access Control (RBAC) Middleware
"""
from functools import wraps
from fastapi import HTTPException, status
from models.models import User


class RBACMiddleware:
    """
    RBAC Middleware for role-based access control
    """
    
    @staticmethod
    def require_role(allowed_roles: list):
        """
        Decorator factory for role-based access control
        
        Args:
            allowed_roles: List of allowed roles (e.g., ["admin", "user"])
        
        Usage:
            @require_role(["admin"])
            def admin_only_function(current_user: User = Depends(get_current_active_user)):
                pass
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, current_user: User = None, **kwargs):
                if current_user is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                if current_user.role not in allowed_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                    )
                
                return await func(*args, current_user=current_user, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def check_permission(user: User, resource_user_id: str) -> bool:
        """
        Check if user has permission to access a resource
        
        Args:
            user: Current user
            resource_user_id: User ID of the resource owner
        
        Returns:
            True if user has permission, False otherwise
        """
        # Admin can access everything
        if user.role == "admin":
            return True
        
        # User can only access their own resources
        return user.id == resource_user_id
    
    @staticmethod
    def is_admin(user: User) -> bool:
        """
        Check if user is admin
        
        Args:
            user: User to check
        
        Returns:
            True if user is admin, False otherwise
        """
        return user.role == "admin"
    
    @staticmethod
    def is_user(user: User) -> bool:
        """
        Check if user has user role
        
        Args:
            user: User to check
        
        Returns:
            True if user has user role, False otherwise
        """
        return user.role == "user"


# Convenience function for checking access
def check_resource_access(current_user: User, resource_user_id: str):
    """
    Check if current user can access a resource
    Raises HTTPException if not authorized
    
    Args:
        current_user: Current authenticated user
        resource_user_id: User ID of the resource owner
    """
    if not RBACMiddleware.check_permission(current_user, resource_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )


def require_admin(current_user: User):
    """
    Require admin role
    Raises HTTPException if not admin
    
    Args:
        current_user: Current authenticated user
    """
    if not RBACMiddleware.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

