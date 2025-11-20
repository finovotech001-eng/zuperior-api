from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.schemas import (
    WalletResponse,
    WalletCreate,
    WalletUpdate,
    PaginatedResponse
)
from app.crud.crud import wallet_crud
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
    search: Optional[str] = Query(None)
):
    """
    List wallets for current user with pagination and filtering
    Note: Each user has only one wallet (one-to-one relationship)
    """
    result = wallet_crud.get_multi(
        db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        filters={},
        search=search,
        search_fields=["walletNumber", "currency"],
        user_id=current_user.id
    )
    
    # Convert SQLAlchemy objects to Pydantic models
    result['items'] = [WalletResponse.model_validate(item) for item in result['items']]
    
    return result


@router.get("/me", response_model=WalletResponse)
def get_my_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's wallet (one-to-one relationship)
    """
    wallet = wallet_crud.get_by_user_id(db, user_id=current_user.id)
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found for this user"
        )
    
    return wallet


@router.get("/{wallet_id}", response_model=WalletResponse)
def get_wallet(
    wallet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get wallet by ID
    """
    wallet = wallet_crud.get_by_id(db, id=wallet_id)
    
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


@router.post("/", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
def create_wallet(
    wallet_in: WalletCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new wallet for current user
    Note: Each user can only have one wallet (one-to-one relationship)
    """
    # Check if wallet already exists for user
    existing_wallet = wallet_crud.get_by_user_id(db, user_id=current_user.id)
    
    if existing_wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet already exists for this user"
        )
    
    wallet = wallet_crud.create(db, obj_in=wallet_in, userId=current_user.id)
    return wallet


@router.put("/{wallet_id}", response_model=WalletResponse)
def update_wallet(
    wallet_id: str,
    wallet_update: WalletUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update wallet
    """
    wallet = wallet_crud.get_by_id(db, id=wallet_id)
    
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
    
    updated_wallet = wallet_crud.update(db, db_obj=wallet, obj_in=wallet_update)
    return updated_wallet


@router.patch("/{wallet_id}/balance", response_model=WalletResponse)
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
    wallet = wallet_crud.get_by_id(db, id=wallet_id)
    
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
    
    updated_wallet = wallet_crud.update_balance(
        db,
        wallet_id=wallet_id,
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
    Delete wallet
    """
    wallet = wallet_crud.get_by_id(db, id=wallet_id)
    
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
    
    wallet_crud.delete(db, id=wallet_id)
    return None

