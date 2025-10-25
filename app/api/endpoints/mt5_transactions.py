from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from core.database import get_db
from api.deps import get_current_active_user
from schemas.schemas import (
    MT5TransactionResponse,
    MT5TransactionCreate,
    MT5TransactionUpdate,
    PaginatedResponse
)
from crud.crud import mt5_transaction_crud, mt5_account_crud
from models.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_mt5_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    order: str = Query("desc", regex="^(asc|desc)$"),
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    List MT5 transactions for current user's MT5 accounts with pagination and filtering
    """
    # Get user's MT5 account IDs
    user_mt5_accounts = mt5_account_crud.get_multi(
        db,
        user_id=current_user.id,
        page=1,
        per_page=1000  # Get all user's accounts
    )
    
    mt5_account_ids = [acc.id for acc in user_mt5_accounts["items"]]
    
    # Build filters
    filters: Dict[str, Any] = {}
    if status:
        filters["status"] = status
    if type:
        filters["type"] = type
    if currency:
        filters["currency"] = currency
    
    # Query transactions
    query = db.query(mt5_transaction_crud.model)
    
    # Filter by user's MT5 accounts
    if mt5_account_ids:
        query = query.filter(mt5_transaction_crud.model.mt5AccountId.in_(mt5_account_ids))
    else:
        # User has no MT5 accounts
        return {
            "items": [],
            "total": 0,
            "page": page,
            "per_page": per_page,
            "total_pages": 0
        }
    
    # Apply filters
    for field, value in filters.items():
        if hasattr(mt5_transaction_crud.model, field):
            query = query.filter(getattr(mt5_transaction_crud.model, field) == value)
    
    # Apply search
    if search:
        query = query.filter(
            mt5_transaction_crud.model.comment.ilike(f"%{search}%") |
            mt5_transaction_crud.model.transactionId.ilike(f"%{search}%")
        )
    
    # Get total
    total = query.count()
    
    # Apply sorting
    if sort_by and hasattr(mt5_transaction_crud.model, sort_by):
        if order == "asc":
            query = query.order_by(getattr(mt5_transaction_crud.model, sort_by).asc())
        else:
            query = query.order_by(getattr(mt5_transaction_crud.model, sort_by).desc())
    else:
        query = query.order_by(mt5_transaction_crud.model.createdAt.desc())
    
    # Paginate
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()
    
    import math
    total_pages = math.ceil(total / per_page) if per_page > 0 else 0
    
    # Convert SQLAlchemy objects to Pydantic models
    items_response = [MT5TransactionResponse.model_validate(item) for item in items]
    
    return {
        "items": items_response,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


@router.get("/{transaction_id}", response_model=MT5TransactionResponse)
def get_mt5_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get MT5 transaction by ID
    """
    transaction = mt5_transaction_crud.get_by_id(db, id=transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MT5 transaction not found"
        )
    
    # Check if transaction belongs to user's MT5 account
    mt5_account = mt5_account_crud.get_by_id(db, id=transaction.mt5AccountId)
    if not mt5_account or mt5_account.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this transaction"
        )
    
    return transaction


@router.post("/", response_model=MT5TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_mt5_transaction(
    transaction_in: MT5TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new MT5 transaction
    """
    # Verify MT5 account belongs to user
    mt5_account = mt5_account_crud.get_by_id(db, id=transaction_in.mt5AccountId)
    if not mt5_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MT5 account not found"
        )
    
    if mt5_account.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create transaction for this MT5 account"
        )
    
    transaction = mt5_transaction_crud.create(
        db,
        obj_in=transaction_in,
        userId=current_user.id
    )
    return transaction


@router.put("/{transaction_id}", response_model=MT5TransactionResponse)
def update_mt5_transaction(
    transaction_id: str,
    transaction_update: MT5TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update MT5 transaction
    """
    transaction = mt5_transaction_crud.get_by_id(db, id=transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MT5 transaction not found"
        )
    
    # Check if transaction belongs to user's MT5 account
    mt5_account = mt5_account_crud.get_by_id(db, id=transaction.mt5AccountId)
    if not mt5_account or mt5_account.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this transaction"
        )
    
    updated_transaction = mt5_transaction_crud.update(
        db,
        db_obj=transaction,
        obj_in=transaction_update
    )
    return updated_transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mt5_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete MT5 transaction
    """
    transaction = mt5_transaction_crud.get_by_id(db, id=transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MT5 transaction not found"
        )
    
    # Check if transaction belongs to user's MT5 account
    mt5_account = mt5_account_crud.get_by_id(db, id=transaction.mt5AccountId)
    if not mt5_account or mt5_account.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this transaction"
        )
    
    mt5_transaction_crud.delete(db, id=transaction_id)
    return None

