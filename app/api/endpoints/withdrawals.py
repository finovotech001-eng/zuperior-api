from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from core.database import get_db
from api.deps import get_current_active_user
from schemas.schemas import (
    WithdrawalResponse,
    WithdrawalCreate,
    WithdrawalUpdate,
    PaginatedResponse
)
from crud.crud import withdrawal_crud, mt5_account_crud
from models.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_withdrawals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    order: str = Query("desc", regex="^(asc|desc)$"),
    status: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    method: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    List withdrawals for current user with pagination and filtering
    """
    filters: Dict[str, Any] = {}
    if status:
        filters["status"] = status
    if currency:
        filters["currency"] = currency
    if method:
        filters["method"] = method
    
    result = withdrawal_crud.get_multi(
        db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        filters=filters,
        search=search,
        search_fields=["externalTransactionId", "walletAddress"],
        user_id=current_user.id
    )
    
    # Convert SQLAlchemy objects to Pydantic models
    result['items'] = [WithdrawalResponse.model_validate(item) for item in result['items']]
    
    return result


@router.get("/{withdrawal_id}", response_model=WithdrawalResponse)
def get_withdrawal(
    withdrawal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get withdrawal by ID
    """
    withdrawal = withdrawal_crud.get_by_id(db, id=withdrawal_id)
    
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal not found"
        )
    
    if withdrawal.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this withdrawal"
        )
    
    return withdrawal


@router.post("/", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
def create_withdrawal(
    withdrawal_in: WithdrawalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new withdrawal request
    """
    # Verify MT5 account belongs to user
    mt5_account = mt5_account_crud.get_by_id(db, id=withdrawal_in.mt5AccountId)
    if not mt5_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MT5 account not found"
        )
    
    if mt5_account.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create withdrawal for this MT5 account"
        )
    
    withdrawal = withdrawal_crud.create(db, obj_in=withdrawal_in, userId=current_user.id)
    return withdrawal


@router.put("/{withdrawal_id}", response_model=WithdrawalResponse)
def update_withdrawal(
    withdrawal_id: str,
    withdrawal_update: WithdrawalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update withdrawal
    """
    withdrawal = withdrawal_crud.get_by_id(db, id=withdrawal_id)
    
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal not found"
        )
    
    if withdrawal.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this withdrawal"
        )
    
    updated_withdrawal = withdrawal_crud.update(db, db_obj=withdrawal, obj_in=withdrawal_update)
    return updated_withdrawal


@router.delete("/{withdrawal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_withdrawal(
    withdrawal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete withdrawal
    """
    withdrawal = withdrawal_crud.get_by_id(db, id=withdrawal_id)
    
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal not found"
        )
    
    if withdrawal.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this withdrawal"
        )
    
    withdrawal_crud.delete(db, id=withdrawal_id)
    return None

