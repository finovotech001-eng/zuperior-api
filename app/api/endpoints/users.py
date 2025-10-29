from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_password_hash
from app.api.deps import get_current_active_user
from app.schemas.schemas import UserResponse, UserUpdate
from app.crud.crud import user_crud
from app.models.models import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user profile
    Can update name, phone, country, email, and password.
    For forgot password functionality, just send the password field.
    """
    # Check if email is being changed and if it already exists
    if user_update.email and user_update.email != current_user.email:
        existing_user = user_crud.get_by_email(db, email=user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Hash password if provided (for password update/forgot password)
    update_dict = user_update.model_dump(exclude_unset=True)
    if "password" in update_dict and update_dict["password"]:
        update_dict["password"] = get_password_hash(update_dict["password"])
        # Create UserUpdate object with hashed password
        user_update = UserUpdate(**update_dict)
    
    updated_user = user_crud.update(db, db_obj=current_user, obj_in=user_update)
    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user by ID (only own profile)
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )
    
    user = user_crud.get_by_id(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

