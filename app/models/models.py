from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Integer, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


def generate_cuid():
    # Simple CUID-like generation (for clientId)
    return f"c{uuid.uuid4().hex[:24]}"


class User(Base):
    __tablename__ = "User"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    clientId = Column(String, unique=True, nullable=False, default=generate_cuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    country = Column(String, nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    emailVerified = Column(Boolean, default=False)
    lastLoginAt = Column(DateTime(timezone=True), nullable=True, index=True)
    role = Column(String, default="user", nullable=False)
    status = Column(String, default="active", nullable=False, index=True)
    
    # Relationships
    mt5Accounts = relationship("MT5Account", back_populates="user", cascade="all, delete-orphan")
    deposits = relationship("Deposit", back_populates="user", cascade="all, delete-orphan")
    withdrawals = relationship("Withdrawal", back_populates="user", cascade="all, delete-orphan")
    kyc = relationship("KYC", back_populates="user", uselist=False, cascade="all, delete-orphan")
    paymentMethods = relationship("PaymentMethod", back_populates="user", cascade="all, delete-orphan")
    refreshTokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_role_status', 'role', 'status'),
    )


class RefreshToken(Base):
    __tablename__ = "RefreshToken"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expiresAt = Column(DateTime(timezone=True), nullable=False, index=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    revoked = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="refreshTokens")


class KYC(Base):
    __tablename__ = "KYC"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    isDocumentVerified = Column(Boolean, default=False)
    isAddressVerified = Column(Boolean, default=False)
    verificationStatus = Column(String, default="Pending")
    documentReference = Column(String, nullable=True)
    addressReference = Column(String, nullable=True)
    amlReference = Column(String, nullable=True)
    documentSubmittedAt = Column(DateTime(timezone=True), nullable=True)
    addressSubmittedAt = Column(DateTime(timezone=True), nullable=True)
    rejectionReason = Column(String, nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    userId = Column(String, ForeignKey("User.id"), unique=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="kyc")


class MT5Account(Base):
    __tablename__ = "MT5Account"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    accountId = Column(String, unique=True, nullable=False)
    userId = Column(String, ForeignKey("User.id"), nullable=False, index=True)
    password = Column(String, nullable=True)
    leverage = Column(Integer, nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="mt5Accounts")
    deposits = relationship("Deposit", back_populates="mt5Account", cascade="all, delete-orphan")
    withdrawals = relationship("Withdrawal", back_populates="mt5Account", cascade="all, delete-orphan")
    mt5Transactions = relationship("MT5Transaction", back_populates="mt5Account", cascade="all, delete-orphan")


class MT5Transaction(Base):
    __tablename__ = "MT5Transaction"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    type = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending", index=True)
    paymentMethod = Column(String, nullable=True)
    transactionId = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    mt5AccountId = Column(String, ForeignKey("MT5Account.id"), nullable=False, index=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    currency = Column(String, default="USD")
    depositId = Column(String, nullable=True, index=True)
    withdrawalId = Column(String, nullable=True, index=True)
    userId = Column(String, nullable=True, index=True)
    processedBy = Column(String, nullable=True)
    processedAt = Column(DateTime(timezone=True), nullable=True)
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    mt5Account = relationship("MT5Account", back_populates="mt5Transactions")


class Deposit(Base):
    __tablename__ = "Deposit"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id"), nullable=False, index=True)
    mt5AccountId = Column(String, ForeignKey("MT5Account.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    method = Column(String, nullable=False)
    paymentMethod = Column(String, nullable=True)
    transactionHash = Column(String, nullable=True)
    proofFileUrl = Column(String, nullable=True)
    bankDetails = Column(Text, nullable=True)
    cryptoAddress = Column(String, nullable=True)
    depositAddress = Column(String, nullable=True)
    externalTransactionId = Column(String, nullable=True)
    status = Column(String, default="pending", index=True)
    rejectionReason = Column(String, nullable=True)
    approvedBy = Column(String, nullable=True)
    approvedAt = Column(DateTime(timezone=True), nullable=True)
    rejectedAt = Column(DateTime(timezone=True), nullable=True)
    processedAt = Column(DateTime(timezone=True), nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="deposits")
    mt5Account = relationship("MT5Account", back_populates="deposits")


class Withdrawal(Base):
    __tablename__ = "Withdrawal"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id"), nullable=False, index=True)
    mt5AccountId = Column(String, ForeignKey("MT5Account.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    method = Column(String, nullable=False)
    bankDetails = Column(Text, nullable=True)
    cryptoAddress = Column(String, nullable=True)
    status = Column(String, default="pending", index=True)
    rejectionReason = Column(String, nullable=True)
    approvedBy = Column(String, nullable=True)
    approvedAt = Column(DateTime(timezone=True), nullable=True)
    rejectedAt = Column(DateTime(timezone=True), nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    currency = Column(String, default="USD")
    externalTransactionId = Column(String, nullable=True)
    paymentMethod = Column(String, nullable=True)
    processedAt = Column(DateTime(timezone=True), nullable=True)
    walletAddress = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="withdrawals")
    mt5Account = relationship("MT5Account", back_populates="withdrawals")


class PaymentMethod(Base):
    __tablename__ = "PaymentMethod"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id"), nullable=False, index=True)
    address = Column(String, nullable=False)
    currency = Column(String, default="USDT")
    network = Column(String, default="TRC20")
    status = Column(String, default="pending", index=True)
    submittedAt = Column(DateTime(timezone=True), nullable=True)
    approvedAt = Column(DateTime(timezone=True), nullable=True)
    approvedBy = Column(String, nullable=True)
    rejectionReason = Column(String, nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="paymentMethods")

