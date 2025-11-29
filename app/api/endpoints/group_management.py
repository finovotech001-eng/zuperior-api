from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_active_admin
from app.schemas.schemas import (
    GroupManagementResponse,
    GroupManagementCreate,
    GroupManagementUpdate,
    PaginatedResponse
)
from app.crud.crud import group_management_crud
from app.models.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    order: str = Query("asc", regex="^(asc|desc)$"),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    account_type: Optional[str] = Query(None)
):
    """
    List groups with pagination
    """
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    if account_type:
        filters["account_type"] = account_type
        
    result = group_management_crud.get_multi(
        db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        filters=filters,
        search=search,
        search_fields=["group", "dedicated_name"]
    )
    
    # Convert SQLAlchemy objects to Pydantic models
    result['items'] = [GroupManagementResponse.model_validate(item) for item in result['items']]
    
    return result


@router.get("/{group_id}", response_model=GroupManagementResponse)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get group by ID
    """
    group = group_management_crud.get_by_id(db, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return group


@router.post("/", response_model=GroupManagementResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    group_in: GroupManagementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Create new group (Admin only)
    """
    # Check if group name already exists
    existing = group_management_crud.get_by_group(db, group=group_in.group)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group name already exists"
        )
    
    group = group_management_crud.create(db, obj_in=group_in)
    return group


@router.put("/{group_id}", response_model=GroupManagementResponse)
def update_group(
    group_id: int,
    group_update: GroupManagementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Update group (Admin only)
    """
    group = group_management_crud.get_by_id(db, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    updated_group = group_management_crud.update(db, db_obj=group, obj_in=group_update)
    return updated_group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Delete group (Admin only)
    """
    group = group_management_crud.get_by_id(db, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    group_management_crud.delete(db, id=group_id)
    return None
