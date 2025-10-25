from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from core.database import get_db
from api.deps import get_current_active_user
from schemas.schemas import (
    DepositResponse,
    DepositCreate,
    DepositUpdate,
    PaginatedResponse
)
from crud.crud import deposit_crud, mt5_account_crud
from models.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_deposits(
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
    List deposits for current user with pagination and filtering
    """
    filters: Dict[str, Any] = {}
    if status:
        filters["status"] = status
    if currency:
        filters["currency"] = currency
    if method:
        filters["method"] = method
    
    result = deposit_crud.get_multi(
        db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        filters=filters,
        search=search,
        search_fields=["transactionHash", "externalTransactionId"],
        user_id=current_user.id
    )
    
    # Convert SQLAlchemy objects to Pydantic models
    result['items'] = [DepositResponse.model_validate(item) for item in result['items']]
    
    return result


@router.get("/{deposit_id}", response_model=DepositResponse)
def get_deposit(
    deposit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get deposit by ID
    """
    deposit = deposit_crud.get_by_id(db, id=deposit_id)
    
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    if deposit.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this deposit"
        )
    
    return deposit


@router.post("/", response_model=DepositResponse, status_code=status.HTTP_201_CREATED)
def create_deposit(
    deposit_in: DepositCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new deposit
    """
    # Verify MT5 account belongs to user
    mt5_account = mt5_account_crud.get_by_id(db, id=deposit_in.mt5AccountId)
    if not mt5_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MT5 account not found"
        )
    
    if mt5_account.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create deposit for this MT5 account"
        )
    
    deposit = deposit_crud.create(db, obj_in=deposit_in, userId=current_user.id)
    return deposit


@router.put("/{deposit_id}", response_model=DepositResponse)
def update_deposit(
    deposit_id: str,
    deposit_update: DepositUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update deposit
    """
    deposit = deposit_crud.get_by_id(db, id=deposit_id)
    
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    if deposit.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this deposit"
        )
    
    updated_deposit = deposit_crud.update(db, db_obj=deposit, obj_in=deposit_update)
    return updated_deposit


@router.delete("/{deposit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deposit(
    deposit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete deposit
    """
    deposit = deposit_crud.get_by_id(db, id=deposit_id)
    
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    if deposit.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this deposit"
        )
    
    deposit_crud.delete(db, id=deposit_id)
    return None

