from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.schemas import (
    DepositResponse,
    DepositCreate,
    DepositUpdate,
    PaginatedResponse,
    CregisDepositRequest,
    CregisDepositResponse,
    CregisCallbackRequest,
    PaymentInfoItem
)
from app.crud.crud import deposit_crud, mt5_account_crud, mt5_transaction_crud
from app.models.models import User, Deposit, MT5Transaction
from app.services.cregis_service import cregis_service
from app.services.mt5_service import mt5_service
from app.core.config import settings

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


@router.post("/cregis-crypto", response_model=CregisDepositResponse, status_code=status.HTTP_201_CREATED)
def create_cregis_crypto_deposit(
    request: CregisDepositRequest,
    req: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a Cregis USDT-TRC20 deposit for mobile app
    
    Creates a deposit order with Cregis and returns payment info with QR code
    for mobile app to display.
    """
    try:
        # Validate MT5 account belongs to user
        mt5_account = mt5_account_crud.get_by_id(db, id=request.mt5AccountId)
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
        
        # Validate amount
        try:
            amount_float = float(request.amount)
            if amount_float <= 0:
                raise ValueError("Amount must be greater than 0")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid amount: {str(e)}"
            )
        
        # Prepare callback URL
        base_url = str(req.base_url).rstrip('/')
        callback_url = f"{base_url}{settings.API_V1_STR}/deposits/cregis-callback"
        success_url = f"{settings.CLIENT_URL}/deposit/success"
        cancel_url = f"{settings.CLIENT_URL}/deposit/cancel"
        
        # Create payment order with Cregis
        cregis_result = cregis_service.create_payment_order(
            order_amount=request.amount,
            order_currency=request.currency,
            callback_url=callback_url,
            success_url=success_url,
            cancel_url=cancel_url,
            payer_id=current_user.clientId,
            valid_time=30  # 30 minutes
        )
        
        if not cregis_result.get("success"):
            error_msg = cregis_result.get("error", "Unknown error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create Cregis payment order: {error_msg}"
            )
        
        cregis_data = cregis_result["data"]
        order_id = cregis_data.get("orderId")  # This is our order_id (third_party_id)
        cregis_id = cregis_data.get("cregis_id")
        payment_info = cregis_data.get("payment_info", [])
        expire_time = cregis_data.get("expire_time")
        
        if not payment_info or len(payment_info) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cregis did not return payment information"
            )
        
        # Extract deposit address from first payment_info item
        deposit_address = payment_info[0].get("address") if payment_info else None
        
        # Create deposit record
        deposit_data = DepositCreate(
            mt5AccountId=request.mt5AccountId,
            amount=amount_float,
            currency=request.currency,
            method="crypto",
            paymentMethod="cregis_usdt",
            depositAddress=deposit_address,
            externalTransactionId=order_id,  # Store order_id for callback matching
        )
        
        deposit = deposit_crud.create(db, obj_in=deposit_data, userId=current_user.id)
        
        # Create MT5Transaction record
        from app.schemas.schemas import MT5TransactionCreate
        mt5_transaction_data = MT5TransactionCreate(
            mt5AccountId=request.mt5AccountId,
            type="Deposit",
            amount=amount_float,
            currency=request.currency,
            paymentMethod="cregis_usdt",
            comment=f"Cregis {request.currency} deposit - {order_id}",
        )
        
        mt5_transaction = mt5_transaction_crud.create(
            db,
            obj_in=mt5_transaction_data,
            userId=current_user.id,
            depositId=deposit.id,
            status="pending",
            transactionId=order_id
        )
        
        # Prepare payment_info for response (with QR codes)
        response_payment_info = []
        for info in payment_info:
            response_payment_info.append(
                PaymentInfoItem(
                    currency=info.get("currency", request.currency),
                    network=info.get("network", "TRC20"),
                    address=info.get("address", deposit_address),
                    amount=info.get("amount", request.amount),
                    qr_code=info.get("qr_code")  # QR code is already in base64 from Cregis
                )
            )
        
        # Return response for mobile app
        return CregisDepositResponse(
            id=deposit.id,
            amount=request.amount,
            currency=request.currency,
            payment_info=response_payment_info,
            expire_time=expire_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/cregis-callback", status_code=status.HTTP_200_OK)
def handle_cregis_callback(
    request: Request,
    callback_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Handle Cregis payment callback (webhook)
    
    This endpoint is called by Cregis when payment status changes.
    No authentication required - signature verification is used instead.
    """
    try:
        # Extract callback data
        cregis_id = callback_data.get("cregis_id")
        third_party_id = callback_data.get("third_party_id")
        status_value = callback_data.get("status", "").lower()
        order_amount = callback_data.get("order_amount")
        order_currency = callback_data.get("order_currency")
        received_amount = callback_data.get("received_amount")
        tx_hash = callback_data.get("tx_hash") or callback_data.get("txid")
        to_address = callback_data.get("to_address")
        payment_detail = callback_data.get("payment_detail", [])
        received_sign = callback_data.get("sign")
        
        # Verify signature
        if received_sign:
            callback_params = {k: v for k, v in callback_data.items() if k != "sign"}
            is_valid = cregis_service.verify_callback_signature(
                callback_params,
                received_sign
            )
            
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid signature"
                )
        
        # Extract additional data from payment_detail if needed
        actual_received_amount = received_amount
        actual_tx_hash = tx_hash
        
        if payment_detail and isinstance(payment_detail, list) and len(payment_detail) > 0:
            first_detail = payment_detail[0]
            if not actual_received_amount:
                actual_received_amount = first_detail.get("receive_amount") or first_detail.get("pay_amount")
            if not actual_tx_hash:
                actual_tx_hash = first_detail.get("tx_id") or first_detail.get("txid")
        
        # Find deposit by externalTransactionId (order_id)
        deposit = db.query(Deposit).filter(
            Deposit.externalTransactionId.in_([cregis_id, third_party_id])
        ).first()
        
        if not deposit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deposit not found for cregis_id={cregis_id}, third_party_id={third_party_id}"
            )
        
        # Map Cregis status to deposit status
        def map_cregis_status(cregis_status: str) -> str:
            status_lower = cregis_status.lower()
            if status_lower in ["paid", "complete", "success", "confirmed"]:
                return "approved"
            elif status_lower in ["rejected", "failed", "cancelled", "expired"]:
                return "rejected"
            return "pending"
        
        mapped_status = map_cregis_status(status_value)
        
        # Prepare update data
        update_data = {
            "status": mapped_status,
        }
        
        if actual_tx_hash:
            update_data["transactionHash"] = actual_tx_hash
        
        if to_address:
            update_data["depositAddress"] = to_address
        
        # Update timestamps based on status
        now = datetime.now(timezone.utc)
        if mapped_status == "approved":
            update_data["approvedAt"] = now
            update_data["processedAt"] = now
        elif mapped_status == "rejected":
            update_data["rejectedAt"] = now
            update_data["rejectionReason"] = f"Cregis status: {status_value}"
        
        # Update deposit
        deposit = deposit_crud.update(db, db_obj=deposit, obj_in=DepositUpdate(**update_data))
        
        # Get MT5 account for later use
        mt5_account = mt5_account_crud.get_by_id(db, id=deposit.mt5AccountId)
        
        # Update or create MT5Transaction record
        mt5_transaction = db.query(MT5Transaction).filter(
            MT5Transaction.depositId == deposit.id
        ).first()
        
        mt5_transaction_update = {
            "status": mapped_status,
        }
        
        if actual_tx_hash:
            mt5_transaction_update["transactionId"] = actual_tx_hash
        
        if mapped_status == "approved":
            mt5_transaction_update["processedAt"] = now
            mt5_transaction_update["processedBy"] = "cregis_webhook"
            mt5_transaction_update["comment"] = f"Cregis deposit confirmed - {deposit.id}"
        
        if mt5_transaction:
            from app.schemas.schemas import MT5TransactionUpdate
            mt5_transaction = mt5_transaction_crud.update(
                db,
                db_obj=mt5_transaction,
                obj_in=MT5TransactionUpdate(**mt5_transaction_update)
            )
        else:
            # Create MT5Transaction if it doesn't exist
            from app.schemas.schemas import MT5TransactionCreate
            mt5_transaction_data = MT5TransactionCreate(
                mt5AccountId=deposit.mt5AccountId,
                type="Deposit",
                amount=deposit.amount,
                currency=order_currency or deposit.currency or "USD",
                paymentMethod=deposit.paymentMethod or "cregis_usdt",
                comment=f"Cregis deposit - {cregis_id or third_party_id}",
            )
            mt5_transaction = mt5_transaction_crud.create(
                db,
                obj_in=mt5_transaction_data,
                userId=deposit.userId,
                depositId=deposit.id,
                status=mapped_status,
                transactionId=actual_tx_hash or deposit.transactionHash
            )
        
        # If payment is approved, credit MT5 balance
        if mapped_status == "approved":
            try:
                # Use actual received amount if available, otherwise use order amount or deposit amount
                amount_to_credit = actual_received_amount
                if not amount_to_credit:
                    amount_to_credit = order_amount or str(deposit.amount)
                
                try:
                    amount_float = float(amount_to_credit)
                except (ValueError, TypeError):
                    amount_float = deposit.amount
                
                # Get MT5 account login
                if not mt5_account or not mt5_account.accountId:
                    raise ValueError(f"MT5 accountId is missing for deposit {deposit.id}")
                
                mt5_login = str(mt5_account.accountId).strip()
                
                # Credit MT5 balance
                mt5_response = mt5_service.add_client_balance(
                    login=mt5_login,
                    balance=amount_float,
                    comment=f"Cregis deposit confirmed - {deposit.id}"
                )
                
                if mt5_response.get("Success"):
                    # Update deposit and MT5Transaction to completed
                    deposit = deposit_crud.update(
                        db,
                        db_obj=deposit,
                        obj_in=DepositUpdate(status="completed")
                    )
                    
                    mt5_transaction = mt5_transaction_crud.update(
                        db,
                        db_obj=mt5_transaction,
                        obj_in=MT5TransactionUpdate(status="completed")
                    )
                else:
                    error_msg = mt5_response.get("Message", "Unknown error")
                    # Update deposit to failed
                    deposit = deposit_crud.update(
                        db,
                        db_obj=deposit,
                        obj_in=DepositUpdate(
                            status="failed",
                            rejectionReason=f"MT5 AddClientBalance failed: {error_msg}"
                        )
                    )
                    
                    if mt5_transaction:
                        mt5_transaction = mt5_transaction_crud.update(
                            db,
                            db_obj=mt5_transaction,
                            obj_in=MT5TransactionUpdate(
                                status="failed",
                                comment=f"MT5 AddClientBalance failed: {error_msg}"
                            )
                        )
                    
            except Exception as mt5_error:
                # Log error but don't fail the callback
                error_msg = str(mt5_error)
                deposit = deposit_crud.update(
                    db,
                    db_obj=deposit,
                    obj_in=DepositUpdate(
                        status="failed",
                        rejectionReason=f"MT5 API error: {error_msg}"
                    )
                )
                
                # Update MT5Transaction if it exists
                if mt5_transaction:
                    mt5_transaction = mt5_transaction_crud.update(
                        db,
                        db_obj=mt5_transaction,
                        obj_in=MT5TransactionUpdate(
                            status="failed",
                            comment=f"MT5 API error: {error_msg}"
                        )
                    )
        
        return {
            "success": True,
            "message": "Callback processed successfully",
            "data": {
                "depositId": deposit.id,
                "status": deposit.status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing callback: {str(e)}"
        )

