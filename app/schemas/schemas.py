import json
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Optional, List, Any, Dict
from datetime import datetime


# ============ Token Schemas ============
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


# ============ Pagination Schema ============
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int


# ============ User Schemas ============
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: Optional[str] = "user"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(UserBase):
    id: str
    clientId: str
    createdAt: datetime
    emailVerified: bool
    lastLoginAt: Optional[datetime] = None
    role: str
    status: str
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    deviceName: Optional[str] = None


# ============ Password Reset Schemas ============
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    newPassword: str = Field(..., min_length=6)


class MessageResponse(BaseModel):
    message: str


class LogoutAllResponse(BaseModel):
    message: str
    sessions_revoked: int


class ActiveSession(BaseModel):
    id: str
    device: Optional[str]
    browser: Optional[str]
    ipAddress: Optional[str]
    createdAt: datetime
    lastActivity: datetime


class ActiveSessionsResponse(BaseModel):
    success: bool
    data: dict
    count: int


# ============ KYC Schemas ============
class KYCBase(BaseModel):
    documentReference: Optional[str] = None
    addressReference: Optional[str] = None
    amlReference: Optional[str] = None


class KYCCreate(KYCBase):
    isDocumentVerified: Optional[bool] = None
    isAddressVerified: Optional[bool] = None
    verificationStatus: Optional[str] = None


class KYCUpdate(KYCBase):
    isDocumentVerified: Optional[bool] = None
    isAddressVerified: Optional[bool] = None
    verificationStatus: Optional[str] = None
    rejectionReason: Optional[str] = None


class KYCResponse(KYCBase):
    id: str
    userId: str
    isDocumentVerified: bool
    isAddressVerified: bool
    verificationStatus: str
    documentSubmittedAt: Optional[datetime] = None
    addressSubmittedAt: Optional[datetime] = None
    rejectionReason: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ MT5Account Schemas ============
class MT5AccountBase(BaseModel):
    accountId: str


class MT5AccountCreate(MT5AccountBase):
    password: Optional[str] = None
    leverage: Optional[int] = None
    accountType: Optional[str] = "Live"
    nameOnAccount: Optional[str] = None
    package: Optional[str] = None


class MT5AccountUpdate(BaseModel):
    accountId: Optional[str] = None
    password: Optional[str] = None
    leverage: Optional[int] = None
    accountType: Optional[str] = None
    nameOnAccount: Optional[str] = None
    package: Optional[str] = None


class MT5AccountResponse(MT5AccountBase):
    id: str
    userId: Optional[str] = None
    accountType: str
    password: Optional[str] = None
    leverage: Optional[int] = None
    nameOnAccount: Optional[str] = None
    package: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ MT5Transaction Schemas ============
class MT5TransactionBase(BaseModel):
    type: str
    amount: float
    currency: Optional[str] = "USD"
    paymentMethod: Optional[str] = None
    comment: Optional[str] = None


class MT5TransactionCreate(MT5TransactionBase):
    mt5AccountId: str


class MT5TransactionUpdate(BaseModel):
    type: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    paymentMethod: Optional[str] = None
    comment: Optional[str] = None


class MT5TransactionResponse(MT5TransactionBase):
    id: str
    mt5AccountId: str
    status: str
    transactionId: Optional[str] = None
    depositId: Optional[str] = None
    withdrawalId: Optional[str] = None
    userId: Optional[str] = None
    processedBy: Optional[str] = None
    processedAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ Deposit Schemas ============
class DepositBase(BaseModel):
    amount: float
    currency: Optional[str] = "USD"
    method: str
    paymentMethod: Optional[str] = None
    transactionHash: Optional[str] = None
    proofFileUrl: Optional[str] = None
    bankDetails: Optional[str] = None
    cryptoAddress: Optional[str] = None
    depositAddress: Optional[str] = None


class DepositCreate(DepositBase):
    mt5AccountId: str


class DepositUpdate(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None
    method: Optional[str] = None
    paymentMethod: Optional[str] = None
    transactionHash: Optional[str] = None
    proofFileUrl: Optional[str] = None
    bankDetails: Optional[str] = None
    cryptoAddress: Optional[str] = None
    depositAddress: Optional[str] = None
    status: Optional[str] = None


class DepositResponse(DepositBase):
    id: str
    userId: str
    mt5AccountId: str
    status: str
    externalTransactionId: Optional[str] = None
    rejectionReason: Optional[str] = None
    approvedBy: Optional[str] = None
    approvedAt: Optional[datetime] = None
    rejectedAt: Optional[datetime] = None
    processedAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ Cregis Deposit Schemas ============
class CregisDepositRequest(BaseModel):
    mt5AccountId: str
    amount: str  # Amount as string (e.g., "100.00")
    currency: str = "USDT"


class PaymentInfoItem(BaseModel):
    currency: str
    network: str
    address: str
    amount: str
    qr_code: Optional[str] = None


class CregisDepositResponse(BaseModel):
    id: str
    amount: str
    currency: str
    payment_info: List[PaymentInfoItem]
    expire_time: int


class CregisCallbackRequest(BaseModel):
    cregis_id: Optional[str] = None
    third_party_id: Optional[str] = None
    status: str
    order_amount: Optional[str] = None
    order_currency: Optional[str] = None
    received_amount: Optional[str] = None
    paid_currency: Optional[str] = None
    txid: Optional[str] = None
    tx_hash: Optional[str] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    block_height: Optional[int] = None
    block_time: Optional[int] = None
    payment_detail: Optional[List[Dict[str, Any]]] = None
    sign: Optional[str] = None


# ============ Withdrawal Schemas ============
class WithdrawalBase(BaseModel):
    amount: float
    method: str
    currency: Optional[str] = "USD"
    bankDetails: Optional[str] = None
    cryptoAddress: Optional[str] = None
    paymentMethod: Optional[str] = None
    walletAddress: Optional[str] = None


class WithdrawalCreate(WithdrawalBase):
    mt5AccountId: Optional[str] = None  # Optional - wallet withdrawals won't have this
    walletId: Optional[str] = None


class WithdrawalUpdate(BaseModel):
    amount: Optional[float] = None
    method: Optional[str] = None
    currency: Optional[str] = None
    bankDetails: Optional[str] = None
    cryptoAddress: Optional[str] = None
    paymentMethod: Optional[str] = None
    walletAddress: Optional[str] = None
    mt5AccountId: Optional[str] = None
    walletId: Optional[str] = None
    status: Optional[str] = None


class WithdrawalResponse(WithdrawalBase):
    id: str
    userId: str
    mt5AccountId: Optional[str] = None  # Optional - wallet withdrawals won't have this
    walletId: Optional[str] = None
    status: str
    externalTransactionId: Optional[str] = None
    rejectionReason: Optional[str] = None
    approvedBy: Optional[str] = None
    approvedAt: Optional[datetime] = None
    rejectedAt: Optional[datetime] = None
    processedAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ PaymentMethod Schemas ============
class PaymentMethodBase(BaseModel):
    # For crypto methods
    address: Optional[str] = None
    currency: Optional[str] = "USDT"
    network: Optional[str] = "TRC20"
    # Type of method: 'crypto' or 'bank'
    methodType: Optional[str] = "crypto"
    # Bank fields (nullable for crypto methods)
    bankName: Optional[str] = None
    accountName: Optional[str] = None
    accountNumber: Optional[str] = None
    ifscSwiftCode: Optional[str] = None
    accountType: Optional[str] = None


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethodUpdate(BaseModel):
    address: Optional[str] = None
    currency: Optional[str] = None
    network: Optional[str] = None
    methodType: Optional[str] = None
    bankName: Optional[str] = None
    accountName: Optional[str] = None
    accountNumber: Optional[str] = None
    ifscSwiftCode: Optional[str] = None
    accountType: Optional[str] = None
    status: Optional[str] = None


class PaymentMethodResponse(PaymentMethodBase):
    id: str
    userId: str
    status: str
    submittedAt: Optional[datetime] = None
    approvedAt: Optional[datetime] = None
    approvedBy: Optional[str] = None
    rejectionReason: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ Account (Wallet) Schemas ============
class AccountBase(BaseModel):
    accountType: str
    balance: Optional[float] = 0.0


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    accountType: Optional[str] = None
    balance: Optional[float] = None


class AccountResponse(AccountBase):
    id: str
    userId: str
    balance: float
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ Wallet Schemas ============
class WalletBase(BaseModel):
    balance: Optional[float] = 0.0
    currency: Optional[str] = "USD"
    walletNumber: Optional[str] = None


class WalletCreate(BaseModel):
    currency: Optional[str] = "USD"
    walletNumber: Optional[str] = None


class WalletUpdate(BaseModel):
    balance: Optional[float] = None
    currency: Optional[str] = None
    walletNumber: Optional[str] = None


class WalletResponse(WalletBase):
    id: str
    userId: str
    balance: float
    currency: str
    walletNumber: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ Transaction Schemas ============
class TransactionBase(BaseModel):
    type: str
    amount: float
    currency: Optional[str] = "USD"
    paymentMethod: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[str] = None  # This maps to metadata_json in the model


class TransactionCreate(TransactionBase):
    depositId: Optional[str] = None
    withdrawalId: Optional[str] = None
    transactionId: Optional[str] = None


class TransactionUpdate(BaseModel):
    type: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    paymentMethod: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[str] = None
    depositId: Optional[str] = None
    withdrawalId: Optional[str] = None
    transactionId: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: str
    userId: str
    status: str
    transactionId: Optional[str] = None
    depositId: Optional[str] = None
    withdrawalId: Optional[str] = None
    metadata: Optional[str] = None  # Will be populated from metadata_json attribute
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def model_validate(cls, obj):
        """Override to map metadata_json attribute to metadata field"""
        # Create a dict from the object attributes
        if hasattr(obj, '__dict__'):
            data = dict(obj.__dict__)
            # Map metadata_json to metadata
            if 'metadata_json' in data and 'metadata' not in data:
                data['metadata'] = data.get('metadata_json')
            # Remove metadata_json from data to avoid conflicts
            data.pop('metadata_json', None)
            # Create a simple object-like structure for validation
            from types import SimpleNamespace
            temp_obj = SimpleNamespace(**data)
            return super().model_validate(temp_obj)
        return super().model_validate(obj)


# ============ WalletTransaction Schemas ============
class WalletTransactionBase(BaseModel):
    type: str
    amount: float
    status: Optional[str] = "completed"
    description: Optional[str] = None
    mt5AccountId: Optional[str] = None
    withdrawalId: Optional[str] = None


class WalletTransactionCreate(WalletTransactionBase):
    walletId: str


class WalletTransactionUpdate(BaseModel):
    type: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None
    mt5AccountId: Optional[str] = None
    withdrawalId: Optional[str] = None


class WalletTransactionResponse(WalletTransactionBase):
    id: str
    walletId: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ Notification Schemas ============
class NotificationBase(BaseModel):
    type: str
    title: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    isRead: Optional[bool] = None


class NotificationResponse(NotificationBase):
    id: str
    userId: str
    isRead: bool
    metadata: Optional[Dict[str, Any]] = None
    createdAt: datetime
    readAt: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def model_validate(cls, obj):
        """Override to map metadata_json attribute to metadata field"""
        if hasattr(obj, '__dict__'):
            data = dict(obj.__dict__)
            if 'metadata_json' in data and 'metadata' not in data:
                data['metadata'] = data.get('metadata_json')
            data.pop('metadata_json', None)
            from types import SimpleNamespace
            temp_obj = SimpleNamespace(**data)
            return super().model_validate(temp_obj)
        return super().model_validate(obj)


# ============ Ticket Schemas ============
class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    ticketType: Optional[str] = None
    priority: Optional[str] = "normal"
    accountNumber: Optional[str] = None
    tags: Optional[List[str]] = None


class TicketCreate(TicketBase):
    """
    Schema for creating a new ticket.
    Accepts both camelCase and snake_case field names for compatibility.
    """
    # Additional fields that can be set during creation (admin-only in practice)
    status: Optional[str] = None
    assignedTo: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,  # Allow both field name and alias
        from_attributes=True
    )
    
    @model_validator(mode='before')
    @classmethod
    def handle_field_names(cls, data: Any) -> Any:
        """
        Convert snake_case field names to camelCase for compatibility.
        Handles both dict and object inputs.
        """
        if isinstance(data, dict):
            # Field name mappings: snake_case -> camelCase
            field_mappings = {
                'ticket_type': 'ticketType',
                'account_number': 'accountNumber',
                'assigned_to': 'assignedTo',
            }
            
            # Convert snake_case to camelCase
            for snake_case, camel_case in field_mappings.items():
                if snake_case in data and camel_case not in data:
                    data[camel_case] = data.pop(snake_case)
        
        return data


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    ticketType: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignedTo: Optional[str] = None
    accountNumber: Optional[str] = None
    tags: Optional[List[str]] = None


class TicketResponse(TicketBase):
    id: int
    ticketNo: str
    userId: str  # Maps to parentId in database
    status: str
    priority: str
    assignedTo: Optional[str] = None
    tags: Optional[List[str]] = None
    createdAt: datetime
    updatedAt: datetime
    lastReplyAt: Optional[datetime] = None
    closedAt: Optional[datetime] = None
    closedBy: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def model_validate(cls, obj):
        """
        Override to handle comprehensive field mapping for TicketResponse.
        
        Handles:
        1. Database column name mappings (snake_case -> camelCase)
        2. Hybrid property mappings (parentId -> userId)
        3. JSON/ARRAY field conversions (tags)
        4. All field transformations needed for Pydantic validation
        """
        if hasattr(obj, '__dict__'):
            data = dict(obj.__dict__)
            
            # Field mapping dictionary: database_column -> model_property
            field_mappings = {
                'ticket_no': 'ticketNo',
                'parent_id': 'parentId',
                'ticket_type': 'ticketType',
                'assigned_to': 'assignedTo',
                'account_number': 'accountNumber',
                'created_at': 'createdAt',
                'updated_at': 'updatedAt',
                'last_reply_at': 'lastReplyAt',
                'closed_at': 'closedAt',
                'closed_by': 'closedBy',
            }
            
            # Apply field mappings (snake_case -> camelCase)
            for db_col, model_prop in field_mappings.items():
                if db_col in data and model_prop not in data:
                    data[model_prop] = data.pop(db_col)
            
            # Handle tags: convert JSON string to list if needed
            if 'tags' in data:
                if isinstance(data['tags'], str):
                    import json
                    try:
                        data['tags'] = json.loads(data['tags'])
                    except:
                        data['tags'] = []
                elif data['tags'] is None:
                    data['tags'] = []
            
            # Map parentId to userId (hybrid property handling)
            # Priority: 1) hybrid property, 2) parentId field, 3) parent_id field
            if 'userId' not in data:
                if hasattr(obj, 'userId'):
                    try:
                        data['userId'] = obj.userId
                    except:
                        pass
                elif 'parentId' in data:
                    data['userId'] = data['parentId']
                elif 'parent_id' in data:
                    data['userId'] = data['parent_id']
            
            # Clean up SQLAlchemy internal attributes
            data.pop('_sa_instance_state', None)
            
            from types import SimpleNamespace
            temp_obj = SimpleNamespace(**data)
            return super().model_validate(temp_obj)
        return super().model_validate(obj)


# ============ Ticket Reply Schemas ============
class TicketReplyBase(BaseModel):
    content: str
    senderName: Optional[str] = None
    senderType: Optional[str] = "user"
    isInternal: Optional[bool] = False
    attachments: Optional[List[str]] = None
    replyId: Optional[int] = None  # For nested replies


class TicketReplyCreate(TicketReplyBase):
    pass


class TicketReplyUpdate(BaseModel):
    content: Optional[str] = None
    isInternal: Optional[bool] = None
    attachments: Optional[List[str]] = None


class TicketReplyResponse(TicketReplyBase):
    id: int
    ticketId: int
    userId: str  # Maps to senderId in database
    senderName: str
    senderType: str
    isInternal: bool
    attachments: Optional[List[str]] = None
    isRead: bool
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def model_validate(cls, obj):
        """
        Override to handle comprehensive field mapping for TicketReplyResponse.
        
        Handles:
        1. Database column name mappings (snake_case -> camelCase)
        2. Hybrid property mappings (senderId -> userId)
        3. JSON/ARRAY field conversions (attachments)
        4. All field transformations needed for Pydantic validation
        """
        if hasattr(obj, '__dict__'):
            data = dict(obj.__dict__)
            
            # Field mapping dictionary: database_column -> model_property
            field_mappings = {
                'ticket_id': 'ticketId',
                'reply_id': 'replyId',
                'sender_id': 'senderId',
                'sender_name': 'senderName',
                'sender_type': 'senderType',
                'is_internal': 'isInternal',
                'created_at': 'createdAt',
                'updated_at': 'updatedAt',
                'is_read': 'isRead',
            }
            
            # Apply field mappings (snake_case -> camelCase)
            for db_col, model_prop in field_mappings.items():
                if db_col in data and model_prop not in data:
                    data[model_prop] = data.pop(db_col)
            
            # Handle attachments: convert JSON string to list if needed
            if 'attachments' in data:
                if isinstance(data['attachments'], str):
                    try:
                        data['attachments'] = json.loads(data['attachments'])
                    except:  # fallback to empty list when JSON parse fails
                        data['attachments'] = []
                elif data['attachments'] is None:
                    data['attachments'] = []
            
            # Map senderId to userId (hybrid property handling)
            # Priority: 1) hybrid property, 2) senderId field, 3) sender_id field
            if 'userId' not in data:
                if hasattr(obj, 'userId'):
                    try:
                        data['userId'] = obj.userId
                    except:
                        pass
                elif 'senderId' in data:
                    data['userId'] = data['senderId']
                elif 'sender_id' in data:
                    data['userId'] = data['sender_id']
            
            from types import SimpleNamespace
            temp_obj = SimpleNamespace(**data)
            return super().model_validate(temp_obj)
        return super().model_validate(obj)


# ============ Country Schemas ============
class CountryBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=2)
    name: str
    phoneCode: Optional[str] = None
    currency: Optional[str] = None
    region: Optional[str] = None
    isActive: Optional[bool] = True


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=2, max_length=2)
    name: Optional[str] = None
    phoneCode: Optional[str] = None
    currency: Optional[str] = None
    region: Optional[str] = None
    isActive: Optional[bool] = None


class CountryResponse(CountryBase):
    id: str
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ Group Management Schemas ============
class GroupManagementBase(BaseModel):
    group: str
    dedicated_name: Optional[str] = None
    account_type: Optional[str] = None
    server: Optional[int] = 1
    auth_mode: Optional[int] = 0
    auth_password_min: Optional[int] = 8
    currency: Optional[str] = None
    leverage: Optional[int] = None
    min_deposit: Optional[float] = None
    spread: Optional[float] = None
    commission: Optional[float] = None
    is_active: Optional[bool] = True


class GroupManagementCreate(GroupManagementBase):
    pass


class GroupManagementUpdate(BaseModel):
    group: Optional[str] = None
    dedicated_name: Optional[str] = None
    account_type: Optional[str] = None
    server: Optional[int] = None
    auth_mode: Optional[int] = None
    auth_password_min: Optional[int] = None
    currency: Optional[str] = None
    leverage: Optional[int] = None
    min_deposit: Optional[float] = None
    spread: Optional[float] = None
    commission: Optional[float] = None
    is_active: Optional[bool] = None


class GroupManagementResponse(GroupManagementBase):
    id: int
    synced_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


