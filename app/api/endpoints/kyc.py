from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.schemas import (
    KYCResponse,
    KYCCreate,
    KYCUpdate
)
from app.crud.crud import kyc_crud
from app.models.models import User

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
    existing_kyc = kyc_crud.get_by_user_id(db, user_id=current_user.id)
    
    # Build data (include None to allow overwrites)
    kyc_data = kyc_in.model_dump()
    
    # Set submission timestamps based on what's provided
    if kyc_data.get("documentReference"):
        kyc_data["documentSubmittedAt"] = datetime.now(timezone.utc)
    if kyc_data.get("addressReference"):
        kyc_data["addressSubmittedAt"] = datetime.now(timezone.utc)
    
    # Set initial verification status if not provided
    if not kyc_data.get("verificationStatus"):
        kyc_data["verificationStatus"] = "Pending"
    
    if existing_kyc:
        # Overwrite existing KYC (admin use-case)
        updated_kyc = kyc_crud.update(
            db,
            db_obj=existing_kyc,
            obj_in=KYCUpdate(**kyc_data)
        )
        return updated_kyc
    
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
    Update KYC for current user.
    
    Regular users can only update:
    - documentReference
    - addressReference
    - amlReference
    
    Admins can also update:
    - isDocumentVerified
    - isAddressVerified
    - verificationStatus
    - rejectionReason
    """
    kyc = kyc_crud.get_by_user_id(db, user_id=current_user.id)
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC not found for this user"
        )
    
    # Get update data
    kyc_data = kyc_update.model_dump(exclude_unset=True)
    
    # Admin-only fields check
    admin_only_fields = ['isDocumentVerified', 'isAddressVerified', 'verificationStatus', 'rejectionReason']
    if current_user.role != "admin":
        for field in admin_only_fields:
            if field in kyc_data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Only admins can update {field}"
                )
    
    # Update submission timestamps when references are updated
    if "documentReference" in kyc_data and kyc_data["documentReference"]:
        kyc.documentSubmittedAt = datetime.now(timezone.utc)
        # Reset verification status if document is resubmitted
        if current_user.role != "admin":
            kyc.isDocumentVerified = False
            if kyc.verificationStatus in ["Verified", "Partially Verified"]:
                kyc.verificationStatus = "Pending"
    
    if "addressReference" in kyc_data and kyc_data["addressReference"]:
        kyc.addressSubmittedAt = datetime.now(timezone.utc)
        # Reset verification status if address is resubmitted
        if current_user.role != "admin":
            kyc.isAddressVerified = False
            if kyc.verificationStatus == "Verified":
                kyc.verificationStatus = "Partially Verified" if kyc.isDocumentVerified else "Pending"
    
    # Auto-update verification status based on document/address verification
    if current_user.role == "admin" and ("isDocumentVerified" in kyc_data or "isAddressVerified" in kyc_data):
        # Get current values or new values
        is_doc_verified = kyc_data.get("isDocumentVerified", kyc.isDocumentVerified)
        is_addr_verified = kyc_data.get("isAddressVerified", kyc.isAddressVerified)
        
        # Determine new verification status
        if is_doc_verified and is_addr_verified:
            kyc_data["verificationStatus"] = "Verified"
        elif is_doc_verified or is_addr_verified:
            kyc_data["verificationStatus"] = "Partially Verified"
        elif not is_doc_verified and not is_addr_verified:
            if kyc_data.get("rejectionReason"):
                kyc_data["verificationStatus"] = "Declined"
            else:
                kyc_data["verificationStatus"] = "Pending"
    
    # Update KYC
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
