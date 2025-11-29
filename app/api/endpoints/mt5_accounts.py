from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.schemas import (
    MT5AccountResponse,
    MT5AccountCreate,
    MT5AccountUpdate,
    PaginatedResponse
)
from app.crud.crud import mt5_account_crud, group_management_crud
from app.models.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_mt5_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    order: str = Query("desc", regex="^(asc|desc)$"),
    search: Optional[str] = Query(None),
    group: Optional[str] = Query(None)
):
    """
    List MT5 accounts with pagination
    - Admins can see all accounts
    - Users can only see their own accounts
    """
    filters = {}
    if group:
        filters["package"] = group

    # If user is not admin, restrict to their own accounts
    user_id = None
    if current_user.role != "admin":
        user_id = current_user.id
        
    result = mt5_account_crud.get_multi(
        db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        filters=filters,
        search=search,
        search_fields=["accountId", "nameOnAccount"],
        user_id=user_id
    )
    
    # Convert SQLAlchemy objects to Pydantic models
    result['items'] = [MT5AccountResponse.model_validate(item) for item in result['items']]
    
    return result


@router.get("/{account_id}", response_model=MT5AccountResponse)
def get_mt5_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get MT5 account by ID
    """
    account = mt5_account_crud.get_by_id(db, id=account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MT5 account not found"
        )
    
    # Allow access if user is admin OR if the account belongs to the user
    if current_user.role != "admin" and account.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this MT5 account"
        )
    
    return account


@router.post("/", response_model=MT5AccountResponse, status_code=status.HTTP_201_CREATED)
def create_mt5_account(
    account_in: MT5AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new MT5 account
    """
    # Check if accountId already exists
    existing = mt5_account_crud.get_by_account_id(db, account_id=account_in.accountId)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MT5 account ID already exists"
        )
        
    # Validate package (group) if provided
    if account_in.package:
        group = group_management_crud.get_by_group(db, group=account_in.package)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid package/group: {account_in.package}"
            )
    
    # If admin creates account, they can specify userId, otherwise use current_user.id
    # For now, we assume admin is creating for themselves or we might need to add userId to MT5AccountCreate schema
    # But based on current schema, we'll just use current_user.id
    account = mt5_account_crud.create(db, obj_in=account_in, userId=current_user.id)
    return account


@router.put("/{account_id}", response_model=MT5AccountResponse)
def update_mt5_account(
    account_id: str,
    account_update: MT5AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update MT5 account
    """
    account = mt5_account_crud.get_by_id(db, id=account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MT5 account not found"
        )
    
    # Allow update if user is admin OR if the account belongs to the user
    if current_user.role != "admin" and account.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this MT5 account"
        )
        
    # Validate package (group) if provided
    if account_update.package:
        group = group_management_crud.get_by_group(db, group=account_update.package)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid package/group: {account_update.package}"
            )
    
    updated_account = mt5_account_crud.update(db, db_obj=account, obj_in=account_update)
    return updated_account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mt5_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete MT5 account
    """
    account = mt5_account_crud.get_by_id(db, id=account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MT5 account not found"
        )
    
    # Allow delete if user is admin OR if the account belongs to the user
    if current_user.role != "admin" and account.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this MT5 account"
        )
    
    mt5_account_crud.delete(db, id=account_id)
    return None


