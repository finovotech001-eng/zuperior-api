from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.schemas import (
    WalletTransactionResponse,
    WalletTransactionCreate,
    WalletTransactionUpdate,
    PaginatedResponse
)
from app.crud.crud import wallet_transaction_crud
from app.models.models import User, Wallet

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_wallet_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    order: str = Query("desc", regex="^(asc|desc)$"),
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    wallet_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    List wallet transactions for current user with pagination and filtering
    """
    filters: Dict[str, Any] = {}
    if status:
        filters["status"] = status
    if type:
        filters["type"] = type
    if wallet_id:
        filters["walletId"] = wallet_id
    
    result = wallet_transaction_crud.get_multi(
        db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        filters=filters,
        search=search,
        search_fields=["description"],
        user_id=current_user.id
    )
    
    # Convert SQLAlchemy objects to Pydantic models
    result['items'] = [WalletTransactionResponse.model_validate(item) for item in result['items']]
    
    return result


@router.get("/{transaction_id}", response_model=WalletTransactionResponse)
def get_wallet_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get wallet transaction by ID
    """
    transaction = wallet_transaction_crud.get_by_id(db, id=transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet transaction not found"
        )
    
    if transaction.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this wallet transaction"
        )
    
    return transaction


@router.post("/", response_model=WalletTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_wallet_transaction(
    transaction_in: WalletTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new wallet transaction
    """
    # Verify wallet belongs to user
    wallet = db.query(Wallet).filter(Wallet.id == transaction_in.walletId).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    if wallet.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create transaction for this wallet"
        )
    
    transaction = wallet_transaction_crud.create(
        db, 
        obj_in=transaction_in, 
        userId=current_user.id
    )
    return transaction


@router.put("/{transaction_id}", response_model=WalletTransactionResponse)
def update_wallet_transaction(
    transaction_id: str,
    transaction_update: WalletTransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update wallet transaction
    """
    transaction = wallet_transaction_crud.get_by_id(db, id=transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet transaction not found"
        )
    
    if transaction.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this wallet transaction"
        )
    
    updated_transaction = wallet_transaction_crud.update(
        db, 
        db_obj=transaction, 
        obj_in=transaction_update
    )
    return updated_transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wallet_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete wallet transaction
    """
    transaction = wallet_transaction_crud.get_by_id(db, id=transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet transaction not found"
        )
    
    if transaction.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this wallet transaction"
        )
    
    wallet_transaction_crud.delete(db, id=transaction_id)
    return None

