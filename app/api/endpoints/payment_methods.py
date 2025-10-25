from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.schemas import (
    PaymentMethodResponse,
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaginatedResponse
)
from app.crud.crud import payment_method_crud
from app.models.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_payment_methods(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    order: str = Query("desc", regex="^(asc|desc)$"),
    status: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    network: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    List payment methods for current user with pagination and filtering
    """
    filters: Dict[str, Any] = {}
    if status:
        filters["status"] = status
    if currency:
        filters["currency"] = currency
    if network:
        filters["network"] = network
    
    result = payment_method_crud.get_multi(
        db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        filters=filters,
        search=search,
        search_fields=["address"],
        user_id=current_user.id
    )
    
    # Convert SQLAlchemy objects to Pydantic models
    result['items'] = [PaymentMethodResponse.model_validate(item) for item in result['items']]
    
    return result


@router.get("/{payment_method_id}", response_model=PaymentMethodResponse)
def get_payment_method(
    payment_method_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get payment method by ID
    """
    payment_method = payment_method_crud.get_by_id(db, id=payment_method_id)
    
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    if payment_method.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this payment method"
        )
    
    return payment_method


@router.post("/", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
def create_payment_method(
    payment_method_in: PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new payment method
    """
    payment_method = payment_method_crud.create(
        db,
        obj_in=payment_method_in,
        userId=current_user.id,
        submittedAt=datetime.utcnow()
    )
    return payment_method


@router.put("/{payment_method_id}", response_model=PaymentMethodResponse)
def update_payment_method(
    payment_method_id: str,
    payment_method_update: PaymentMethodUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update payment method
    """
    payment_method = payment_method_crud.get_by_id(db, id=payment_method_id)
    
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    if payment_method.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this payment method"
        )
    
    updated_payment_method = payment_method_crud.update(
        db,
        db_obj=payment_method,
        obj_in=payment_method_update
    )
    return updated_payment_method


@router.delete("/{payment_method_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_method(
    payment_method_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete payment method
    """
    payment_method = payment_method_crud.get_by_id(db, id=payment_method_id)
    
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    if payment_method.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this payment method"
        )
    
    payment_method_crud.delete(db, id=payment_method_id)
    return None

