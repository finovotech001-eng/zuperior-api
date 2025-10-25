from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Any
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


# ============ KYC Schemas ============
class KYCBase(BaseModel):
    documentReference: Optional[str] = None
    addressReference: Optional[str] = None
    amlReference: Optional[str] = None


class KYCCreate(KYCBase):
    pass


class KYCUpdate(KYCBase):
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


class MT5AccountUpdate(BaseModel):
    accountId: Optional[str] = None
    password: Optional[str] = None
    leverage: Optional[int] = None


class MT5AccountResponse(MT5AccountBase):
    id: str
    userId: str
    password: Optional[str] = None
    leverage: Optional[int] = None
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
    mt5AccountId: str


class WithdrawalUpdate(BaseModel):
    amount: Optional[float] = None
    method: Optional[str] = None
    currency: Optional[str] = None
    bankDetails: Optional[str] = None
    cryptoAddress: Optional[str] = None
    paymentMethod: Optional[str] = None
    walletAddress: Optional[str] = None
    status: Optional[str] = None


class WithdrawalResponse(WithdrawalBase):
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


# ============ PaymentMethod Schemas ============
class PaymentMethodBase(BaseModel):
    address: str
    currency: Optional[str] = "USDT"
    network: Optional[str] = "TRC20"


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethodUpdate(BaseModel):
    address: Optional[str] = None
    currency: Optional[str] = None
    network: Optional[str] = None
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



