from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc
from pydantic import BaseModel
from app.core.database import Base
import math

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get_by_id(self, db: Session, id: str) -> Optional[ModelType]:
        """Get a single record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        order: str = "desc",
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        search_fields: Optional[List[str]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get multiple records with pagination, filtering, sorting, and search
        """
        query = db.query(self.model)
        
        # Apply user filter if provided (for user-specific data)
        if user_id and hasattr(self.model, 'userId'):
            query = query.filter(self.model.userId == user_id)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.filter(getattr(self.model, field) == value)
        
        # Apply search
        if search and search_fields:
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    search_conditions.append(
                        getattr(self.model, field).ilike(f"%{search}%")
                    )
            if search_conditions:
                query = query.filter(or_(*search_conditions))
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        if sort_by and hasattr(self.model, sort_by):
            if order.lower() == "asc":
                query = query.order_by(asc(getattr(self.model, sort_by)))
            else:
                query = query.order_by(desc(getattr(self.model, sort_by)))
        else:
            # Default sorting by createdAt if available
            if hasattr(self.model, 'createdAt'):
                query = query.order_by(desc(self.model.createdAt))
        
        # Apply pagination
        offset = (page - 1) * per_page
        items = query.offset(offset).limit(per_page).all()
        
        total_pages = math.ceil(total / per_page) if per_page > 0 else 0
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    
    def create(self, db: Session, *, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        """Create a new record"""
        obj_in_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        obj_in_data.update(kwargs)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update a record"""
        obj_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in.dict(exclude_unset=True)
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, id: str) -> Optional[ModelType]:
        """Delete a record"""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj


# Import models
from app.models.models import (
    User, KYC, MT5Account, MT5Transaction, 
    Deposit, Withdrawal, PaymentMethod
)
from app.schemas.schemas import (
    UserCreate, UserUpdate,
    KYCCreate, KYCUpdate,
    MT5AccountCreate, MT5AccountUpdate,
    MT5TransactionCreate, MT5TransactionUpdate,
    DepositCreate, DepositUpdate,
    WithdrawalCreate, WithdrawalUpdate,
    PaymentMethodCreate, PaymentMethodUpdate
)


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_by_client_id(self, db: Session, client_id: str) -> Optional[User]:
        """Get user by clientId"""
        return db.query(User).filter(User.clientId == client_id).first()


class KYCCRUD(CRUDBase[KYC, KYCCreate, KYCUpdate]):
    def get_by_user_id(self, db: Session, user_id: str) -> Optional[KYC]:
        """Get KYC by user ID"""
        return db.query(KYC).filter(KYC.userId == user_id).first()


class MT5AccountCRUD(CRUDBase[MT5Account, MT5AccountCreate, MT5AccountUpdate]):
    def get_by_account_id(self, db: Session, account_id: str) -> Optional[MT5Account]:
        """Get MT5Account by accountId"""
        return db.query(MT5Account).filter(MT5Account.accountId == account_id).first()


class MT5TransactionCRUD(CRUDBase[MT5Transaction, MT5TransactionCreate, MT5TransactionUpdate]):
    pass


class DepositCRUD(CRUDBase[Deposit, DepositCreate, DepositUpdate]):
    pass


class WithdrawalCRUD(CRUDBase[Withdrawal, WithdrawalCreate, WithdrawalUpdate]):
    pass


class PaymentMethodCRUD(CRUDBase[PaymentMethod, PaymentMethodCreate, PaymentMethodUpdate]):
    pass


# Instantiate CRUD objects
user_crud = UserCRUD(User)
kyc_crud = KYCCRUD(KYC)
mt5_account_crud = MT5AccountCRUD(MT5Account)
mt5_transaction_crud = MT5TransactionCRUD(MT5Transaction)
deposit_crud = DepositCRUD(Deposit)
withdrawal_crud = WithdrawalCRUD(Withdrawal)
payment_method_crud = PaymentMethodCRUD(PaymentMethod)

