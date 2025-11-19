from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Integer, Text, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
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
    resetToken = Column(String, nullable=True, index=True)
    resetTokenExpires = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    activityLogs = relationship("ActivityLog", back_populates="admin", cascade="all, delete-orphan")
    defaultMT5Account = relationship("DefaultMT5Account", back_populates="user", uselist=False, cascade="all, delete-orphan")
    deposits = relationship("Deposit", back_populates="user", cascade="all, delete-orphan")
    kyc = relationship("KYC", back_populates="user", uselist=False, cascade="all, delete-orphan")
    mt5Accounts = relationship("MT5Account", back_populates="user", cascade="all, delete-orphan")
    refreshTokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    userFavorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    withdrawals = relationship("Withdrawal", back_populates="user", cascade="all, delete-orphan")
    userLoginLogs = relationship("UserLoginLog", back_populates="user", cascade="all, delete-orphan")
    wallet = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    walletTransactions = relationship("WalletTransaction", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_role_status', 'role', 'status'),
    )


class RefreshToken(Base):
    __tablename__ = "RefreshToken"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE", onupdate="NO ACTION"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expiresAt = Column(DateTime(timezone=True), nullable=False, index=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    revoked = Column(Boolean, nullable=True)
    deviceName = Column(String, nullable=True)
    ipAddress = Column(String, nullable=True)
    userAgent = Column(String, nullable=True)
    lastActivity = Column(DateTime(timezone=True), server_default=func.now(), nullable=True, index=True)
    
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
    userId = Column(String, ForeignKey("User.id"), nullable=True)
    accountType = Column(String, default="Live", nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    password = Column(String, nullable=True)
    leverage = Column(Integer, nullable=True)
    nameOnAccount = Column(String, nullable=True)
    package = Column(String, nullable=True)
    
    # Relationships
    defaultMT5Accounts = relationship("DefaultMT5Account", back_populates="mt5Account", cascade="all, delete-orphan")
    deposits = relationship("Deposit", back_populates="mt5Account", cascade="all, delete-orphan")
    withdrawals = relationship("Withdrawal", back_populates="mt5Account", cascade="all, delete-orphan")
    user = relationship("User", back_populates="mt5Accounts")
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
    transactions = relationship("Transaction", back_populates="deposit", cascade="all, delete-orphan")


class Withdrawal(Base):
    __tablename__ = "Withdrawal"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id"), nullable=False, index=True)
    mt5AccountId = Column(String, ForeignKey("MT5Account.id"), nullable=True, index=True)  # Optional - wallet withdrawals won't have this
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
    walletId = Column(String, ForeignKey("Wallet.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="withdrawals")
    mt5Account = relationship("MT5Account", back_populates="withdrawals")
    wallet = relationship("Wallet", back_populates="withdrawals")
    transactions = relationship("Transaction", back_populates="withdrawal", cascade="all, delete-orphan")


class PaymentMethod(Base):
    __tablename__ = "PaymentMethod"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id"), nullable=False, index=True)
    # For crypto methods
    address = Column(String, nullable=True)
    currency = Column(String, default="USDT")
    network = Column(String, default="TRC20")
    # Type of method: 'crypto' or 'bank'
    methodType = Column(String, default="crypto")
    # Bank fields (nullable for crypto methods)
    bankName = Column(String, nullable=True)
    accountName = Column(String, nullable=True)
    accountNumber = Column(String, nullable=True)
    ifscSwiftCode = Column(String, nullable=True)
    accountType = Column(String, nullable=True)
    status = Column(String, default="pending", index=True)
    submittedAt = Column(DateTime(timezone=True), server_default=func.now())
    approvedAt = Column(DateTime(timezone=True), nullable=True)
    approvedBy = Column(String, nullable=True)
    rejectionReason = Column(String, nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Account(Base):
    __tablename__ = "Account"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id"), nullable=False, index=True)
    accountType = Column(String, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="accounts")


class Transaction(Base):
    __tablename__ = "Transaction"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending", nullable=False, index=True)
    currency = Column(String, default="USD", nullable=False)
    paymentMethod = Column(String, nullable=True)
    transactionId = Column(String, nullable=True)
    description = Column(String, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)  # Python attr 'metadata_json' maps to DB column 'metadata' to avoid SQLAlchemy reserved word conflict
    depositId = Column(String, ForeignKey("Deposit.id"), nullable=True, index=True)
    withdrawalId = Column(String, ForeignKey("Withdrawal.id"), nullable=True, index=True)
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    deposit = relationship("Deposit", back_populates="transactions")
    withdrawal = relationship("Withdrawal", back_populates="transactions")


class Wallet(Base):
    __tablename__ = "Wallet"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id"), unique=True, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    walletNumber = Column(String, unique=True, nullable=True)
    currency = Column(String, default="USD", nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="wallet")
    withdrawals = relationship("Withdrawal", back_populates="wallet")
    transactions = relationship("WalletTransaction", back_populates="wallet", cascade="all, delete-orphan")


class WalletTransaction(Base):
    __tablename__ = "WalletTransaction"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    walletId = Column(String, ForeignKey("Wallet.id"), nullable=False, index=True)
    userId = Column(String, ForeignKey("User.id"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # e.g., MT5_TO_WALLET, WALLET_WITHDRAWAL
    amount = Column(Float, nullable=False)
    status = Column(String, default="completed", nullable=False)
    description = Column(String, nullable=True)
    mt5AccountId = Column(String, nullable=True)
    withdrawalId = Column(String, nullable=True, index=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    user = relationship("User", back_populates="walletTransactions")


class ActivityLog(Base):
    __tablename__ = "ActivityLog"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, nullable=True)
    adminId = Column(String, ForeignKey("User.id"), nullable=False)
    action = Column(String, nullable=False)
    entity = Column(String, nullable=False)
    entityId = Column(String, nullable=True)
    ipAddress = Column(String, nullable=True)
    userAgent = Column(String, nullable=True)
    oldValues = Column(Text, nullable=True)
    newValues = Column(Text, nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    admin = relationship("User", back_populates="activityLogs", foreign_keys=[adminId])


class DefaultMT5Account(Base):
    __tablename__ = "DefaultMT5Account"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id"), unique=True, nullable=False)
    mt5AccountId = Column(String, ForeignKey("MT5Account.accountId"), nullable=False, index=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="defaultMT5Account")
    mt5Account = relationship("MT5Account", back_populates="defaultMT5Accounts")


class Instrument(Base):
    __tablename__ = "Instrument"
    
    id = Column(String, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)
    group = Column(String, nullable=True)
    digits = Column(Integer, default=5)
    contractSize = Column(Float, default=100000)
    minVolume = Column(Float, default=0.01)
    maxVolume = Column(Float, default=100)
    volumeStep = Column(Float, default=0.01)
    spread = Column(Float, default=0)
    isActive = Column(Boolean, default=True)
    tradingHours = Column(String, nullable=True)
    lastUpdated = Column(DateTime(timezone=True), nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    userFavorites = relationship("UserFavorite", back_populates="instrument", cascade="all, delete-orphan")


class UserFavorite(Base):
    __tablename__ = "UserFavorite"
    
    id = Column(String, primary_key=True)
    userId = Column(String, ForeignKey("User.id"), nullable=False, index=True)
    instrumentId = Column(String, ForeignKey("Instrument.id"), nullable=False, index=True)
    sortOrder = Column(Integer, default=0)
    addedAt = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="userFavorites")
    instrument = relationship("Instrument", back_populates="userFavorites")
    
    __table_args__ = (
        Index('idx_user_favorite_unique', 'userId', 'instrumentId', unique=True),
    )


class UserLoginLog(Base):
    __tablename__ = "UserLoginLog"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False, index=True)
    user_agent = Column(String, nullable=True)
    device = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    success = Column(Boolean, default=True)
    failure_reason = Column(String, nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="userLoginLogs")


class Notification(Base):
    __tablename__ = "Notification"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column("userId", String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)  # deposit, withdrawal, internal_transfer, account_creation, account_update, support_ticket_reply
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    isRead = Column("isRead", Boolean, default=False, index=True)
    metadata_json = Column("metadata", JSON, nullable=True)  # Python attr 'metadata_json' maps to DB column 'metadata' to avoid SQLAlchemy reserved word conflict
    createdAt = Column("createdAt", DateTime(timezone=True), server_default=func.now(), index=True)
    readAt = Column("readAt", DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")

