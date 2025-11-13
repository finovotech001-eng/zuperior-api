from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.schemas import (
    AccountResponse,
    AccountCreate,
    AccountUpdate,
    PaginatedResponse
)
from app.crud.crud import account_crud
from app.models.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_wallets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    order: str = Query("desc", regex="^(asc|desc)$"),
    account_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    List wallets (accounts) for current user with pagination and filtering
    """
    filters: Dict[str, Any] = {}
    if account_type:
        filters["accountType"] = account_type
    
    result = account_crud.get_multi(
        db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        filters=filters,
        search=search,
        search_fields=["accountType"],
        user_id=current_user.id
    )
    
    # Convert SQLAlchemy objects to Pydantic models
    result['items'] = [AccountResponse.model_validate(item) for item in result['items']]
    
    return result


@router.get("/{wallet_id}", response_model=AccountResponse)
def get_wallet(
    wallet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get wallet (account) by ID
    """
    wallet = account_crud.get_by_id(db, id=wallet_id)
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    if wallet.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this wallet"
        )
    
    return wallet


@router.get("/type/{account_type}", response_model=AccountResponse)
def get_wallet_by_type(
    account_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get wallet (account) by account type for current user
    """
    wallet = account_crud.get_by_user_id_and_type(
        db, 
        user_id=current_user.id, 
        account_type=account_type
    )
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet with type '{account_type}' not found"
        )
    
    return wallet


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_wallet(
    wallet_in: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new wallet (account)
    """
    # Check if account with same type already exists for user
    existing_wallet = account_crud.get_by_user_id_and_type(
        db,
        user_id=current_user.id,
        account_type=wallet_in.accountType
    )
    
    if existing_wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wallet with type '{wallet_in.accountType}' already exists"
        )
    
    wallet = account_crud.create(db, obj_in=wallet_in, userId=current_user.id)
    return wallet


@router.put("/{wallet_id}", response_model=AccountResponse)
def update_wallet(
    wallet_id: str,
    wallet_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update wallet (account)
    """
    wallet = account_crud.get_by_id(db, id=wallet_id)
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    if wallet.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this wallet"
        )
    
    # If accountType is being changed, check if new type already exists
    if wallet_update.accountType and wallet_update.accountType != wallet.accountType:
        existing_wallet = account_crud.get_by_user_id_and_type(
            db,
            user_id=current_user.id,
            account_type=wallet_update.accountType
        )
        if existing_wallet and existing_wallet.id != wallet_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Wallet with type '{wallet_update.accountType}' already exists"
            )
    
    updated_wallet = account_crud.update(db, db_obj=wallet, obj_in=wallet_update)
    return updated_wallet


@router.patch("/{wallet_id}/balance", response_model=AccountResponse)
def update_wallet_balance(
    wallet_id: str,
    amount: float = Query(..., description="Amount to add or subtract"),
    operation: str = Query("add", regex="^(add|subtract|set)$", description="Operation: add, subtract, or set"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update wallet balance
    Operations: add, subtract, or set (to a specific amount)
    """
    wallet = account_crud.get_by_id(db, id=wallet_id)
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    if wallet.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this wallet"
        )
    
    updated_wallet = account_crud.update_balance(
        db,
        account_id=wallet_id,
        amount=amount,
        operation=operation
    )
    
    if not updated_wallet:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update wallet balance"
        )
    
    return updated_wallet


@router.delete("/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wallet(
    wallet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete wallet (account)
    """
    wallet = account_crud.get_by_id(db, id=wallet_id)
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    if wallet.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this wallet"
        )
    
    account_crud.delete(db, id=wallet_id)
    return None

