from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth
from app.api.endpoints import (
    users,
    mt5_accounts,
    mt5_transactions,
    deposits,
    withdrawals,
    kyc,
    payment_methods,
    emails
)

# Suppress noisy passlib bcrypt version warning (harmless)
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Create database tables
Base.metadata.create_all(bind=engine)
print("DATABASE_URL:", settings.DATABASE_URL)
print("SECRET_KEY:", settings.SECRET_KEY)
# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": settings.PROJECT_NAME}


# Root endpoint
@app.get("/")
def root():
    """
    Root endpoint
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["Users"]
)

app.include_router(
    mt5_accounts.router,
    prefix=f"{settings.API_V1_STR}/mt5-accounts",
    tags=["MT5 Accounts"]
)

app.include_router(
    mt5_transactions.router,
    prefix=f"{settings.API_V1_STR}/mt5-transactions",
    tags=["MT5 Transactions"]
)

app.include_router(
    deposits.router,
    prefix=f"{settings.API_V1_STR}/deposits",
    tags=["Deposits"]
)

app.include_router(
    withdrawals.router,
    prefix=f"{settings.API_V1_STR}/withdrawals",
    tags=["Withdrawals"]
)

app.include_router(
    kyc.router,
    prefix=f"{settings.API_V1_STR}/kyc",
    tags=["KYC"]
)

app.include_router(
    payment_methods.router,
    prefix=f"{settings.API_V1_STR}/payment-methods",
    tags=["Payment Methods"]
)

app.include_router(
    emails.router,
    prefix=f"{settings.API_V1_STR}/emails",
    tags=["Emails"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
