from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from core.database import get_db
from api.deps import get_current_active_user
from schemas.schemas import (
    KYCResponse,
    KYCCreate,
    KYCUpdate
)
from crud.crud import kyc_crud
from models.models import User

router = APIRouter()


@router.get("/", response_model=KYCResponse)
def get_kyc(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get KYC for current user
    """
    kyc = kyc_crud.get_by_user_id(db, user_id=current_user.id)
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC not found for this user"
        )
    
    return kyc


@router.post("/", response_model=KYCResponse, status_code=status.HTTP_201_CREATED)
def create_kyc(
    kyc_in: KYCCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create or submit KYC for current user
    """
    # Check if KYC already exists
    existing_kyc = kyc_crud.get_by_user_id(db, user_id=current_user.id)
    if existing_kyc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="KYC already exists for this user"
        )
    
    # Set submission timestamps based on what's provided
    kyc_data = kyc_in.model_dump()
    if kyc_data.get("documentReference"):
        kyc_data["documentSubmittedAt"] = datetime.utcnow()
    if kyc_data.get("addressReference"):
        kyc_data["addressSubmittedAt"] = datetime.utcnow()
    
    kyc = kyc_crud.create(
        db,
        obj_in=KYCCreate(**kyc_data),
        userId=current_user.id
    )
    return kyc


@router.put("/", response_model=KYCResponse)
def update_kyc(
    kyc_update: KYCUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update KYC for current user
    """
    kyc = kyc_crud.get_by_user_id(db, user_id=current_user.id)
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC not found for this user"
        )
    
    # Update submission timestamps based on what's being updated
    kyc_data = kyc_update.model_dump(exclude_unset=True)
    if "documentReference" in kyc_data and kyc_data["documentReference"]:
        kyc.documentSubmittedAt = datetime.utcnow()
    if "addressReference" in kyc_data and kyc_data["addressReference"]:
        kyc.addressSubmittedAt = datetime.utcnow()
    
    updated_kyc = kyc_crud.update(db, db_obj=kyc, obj_in=kyc_update)
    return updated_kyc


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_kyc(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete KYC for current user
    """
    kyc = kyc_crud.get_by_user_id(db, user_id=current_user.id)
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC not found for this user"
        )
    
    kyc_crud.delete(db, id=kyc.id)
    return None

