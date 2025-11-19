from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    generate_password_reset_token
)
from app.core.config import settings
from app.schemas.schemas import (
    UserCreate,
    UserResponse,
    Token,
    TokenRefresh,
    UserLogin,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
    LogoutAllResponse,
    ActiveSessionsResponse
)
from app.crud.crud import user_crud
from app.models.models import RefreshToken, User
from app.api.deps import verify_refresh_token, get_current_active_user, get_device_info
from app.services.email_service import send_email_to
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


def send_welcome_email_task(email: str, name: str = None):
    """
    Background task to send welcome email
    """
    try:
        recipient_name = name or 'Trader'
        logo_url = settings.EMAIL_LOGO_URL or f"{settings.CLIENT_URL.rstrip('/')}/logo.png"
        dashboard_url = settings.CLIENT_URL
        
        BRAND_PRIMARY = "#6242a5"
        BRAND_PRIMARY_ALT = "#9f8bcf"
        BORDER_COLOR = "#e5e7eb"
        BG_COLOR = "#f9fafb"
        
        text = f"""Hi {recipient_name},

Welcome to Zuperior! 🎉

We're thrilled to have you join our trading community. Your account has been created successfully.

Get started with these quick steps:
1. Complete your KYC verification to unlock all features
2. Fund your account and start trading
3. Explore our MT5 platform

Need help? Our support team is here for you 24/7.

Happy Trading!
Team Zuperior
"""
        
        html = f'''<!doctype html>
<html>
<head>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <style>
        @media only screen and (max-width: 600px) {{
            .main-table {{
                width: 100% !important;
            }}
            .content-padding {{
                padding: 16px !important;
            }}
        }}
    </style>
</head>
<body style="margin:0;padding:24px;background:{BG_COLOR};font-family:Arial,sans-serif">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:16px;box-shadow:0 4px 6px rgba(0,0,0,0.1)">
        <!-- Header -->
        <tr>
            <td style="background:linear-gradient(135deg,{BRAND_PRIMARY},{BRAND_PRIMARY_ALT});padding:32px 24px;border-radius:16px 16px 0 0">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align:center">
                            <img src="{logo_url}" alt="Zuperior" style="height:32px;margin-bottom:12px" />
                            <div style="font-size:24px;color:#fff;font-weight:700;margin-bottom:4px">Zuperior</div>
                            <div style="font-size:14px;color:rgba(255,255,255,0.9)">Welcome Aboard!</div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <!-- Celebration Icon -->
        <tr>
            <td style="padding:32px 24px 16px;text-align:center">
                <div style="font-size:64px">🎉</div>
            </td>
        </tr>
        
        <!-- Greeting -->
        <tr>
            <td class="content-padding" style="padding:0 24px 16px">
                <div style="font-size:20px;font-weight:600;color:#1f2937;margin-bottom:8px">Hi {recipient_name}!</div>
                <p style="margin:0;font-size:16px;color:#4b5563;line-height:1.6">
                    We're thrilled to have you join our trading community. Your account has been created successfully and you're all set to start your trading journey with us!
                </p>
            </td>
        </tr>
        
        <!-- Quick Steps -->
        <tr>
            <td class="content-padding" style="padding:16px 24px">
                <div style="background:#f8f9fa;border-radius:12px;padding:20px;border-left:4px solid {BRAND_PRIMARY}">
                    <div style="font-size:16px;font-weight:600;color:#1f2937;margin-bottom:12px">Get Started in 3 Easy Steps:</div>
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding:8px 0;vertical-align:top">
                                <div style="display:inline-block;background:{BRAND_PRIMARY};color:#fff;width:24px;height:24px;border-radius:50%;text-align:center;line-height:24px;font-weight:700;font-size:14px;margin-right:12px">1</div>
                                <span style="font-size:14px;color:#374151;line-height:1.6">Complete your KYC verification to unlock all features</span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:8px 0;vertical-align:top">
                                <div style="display:inline-block;background:{BRAND_PRIMARY};color:#fff;width:24px;height:24px;border-radius:50%;text-align:center;line-height:24px;font-weight:700;font-size:14px;margin-right:12px">2</div>
                                <span style="font-size:14px;color:#374151;line-height:1.6">Fund your account with your preferred payment method</span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:8px 0;vertical-align:top">
                                <div style="display:inline-block;background:{BRAND_PRIMARY};color:#fff;width:24px;height:24px;border-radius:50%;text-align:center;line-height:24px;font-weight:700;font-size:14px;margin-right:12px">3</div>
                                <span style="font-size:14px;color:#374151;line-height:1.6">Start trading on our powerful MT5 platform</span>
                            </td>
                        </tr>
                    </table>
                </div>
            </td>
        </tr>
        
        <!-- CTA Button -->
        <tr>
            <td class="content-padding" style="padding:16px 24px 32px;text-align:center">
                <a href="{dashboard_url}" style="display:inline-block;background:linear-gradient(135deg,{BRAND_PRIMARY},{BRAND_PRIMARY_ALT});color:#fff;text-decoration:none;font-weight:600;padding:14px 32px;border-radius:10px;font-size:16px;box-shadow:0 4px 6px rgba(98,66,165,0.3);transition:all 0.3s">
                    Go to Dashboard
                </a>
            </td>
        </tr>
        
        <!-- Support Section -->
        <tr>
            <td class="content-padding" style="padding:16px 24px 24px;border-top:1px solid {BORDER_COLOR}">
                <div style="background:#fef3c7;border-radius:10px;padding:16px;text-align:center">
                    <p style="margin:0;font-size:14px;color:#78350f;line-height:1.6">
                        💬 <strong>Need help?</strong> Our support team is here for you 24/7.<br/>
                        We're committed to making your trading experience exceptional.
                    </p>
                </div>
            </td>
        </tr>
        
        <!-- Footer -->
        <tr>
            <td style="background:#fafafa;padding:20px 24px;font-size:12px;color:#6b7280;border-top:1px solid {BORDER_COLOR};border-radius:0 0 16px 16px">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align:center">
                            <p style="margin:0 0 8px 0">© {datetime.now().year} Zuperior. All rights reserved.</p>
                            <p style="margin:0;font-size:11px">You're receiving this email because you signed up for a Zuperior account.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''
        
        send_email_to(email, "Welcome to Zuperior! 🎉", text, html)
        logger.info(f"Welcome email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {e}")


def send_password_reset_email_task(email: str, name: str, reset_token: str):
    """
    Background task to send password reset email
    """
    try:
        recipient_name = name or 'Trader'
        logo_url = settings.EMAIL_LOGO_URL or f"{settings.CLIENT_URL.rstrip('/')}/logo.png"
        reset_url = f"{settings.CLIENT_URL.rstrip('/')}/reset-password?token={reset_token}"
        
        BRAND_PRIMARY = "#6242a5"
        BRAND_PRIMARY_ALT = "#9f8bcf"
        BORDER_COLOR = "#e5e7eb"
        BG_COLOR = "#f9fafb"
        
        text = f"""Hi {recipient_name},

We received a request to reset your password for your Zuperior account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request this password reset, please ignore this email. Your password will remain unchanged.

For security reasons, never share this link with anyone.

Best regards,
Team Zuperior
"""
        
        html = f'''<!doctype html>
<html>
<head>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <style>
        @media only screen and (max-width: 600px) {{
            .main-table {{
                width: 100% !important;
            }}
            .content-padding {{
                padding: 16px !important;
            }}
        }}
    </style>
</head>
<body style="margin:0;padding:24px;background:{BG_COLOR};font-family:Arial,sans-serif">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:16px;box-shadow:0 4px 6px rgba(0,0,0,0.1)">
        <!-- Header -->
        <tr>
            <td style="background:linear-gradient(135deg,{BRAND_PRIMARY},{BRAND_PRIMARY_ALT});padding:32px 24px;border-radius:16px 16px 0 0">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align:center">
                            <img src="{logo_url}" alt="Zuperior" style="height:32px;margin-bottom:12px" />
                            <div style="font-size:24px;color:#fff;font-weight:700;margin-bottom:4px">Zuperior</div>
                            <div style="font-size:14px;color:rgba(255,255,255,0.9)">Password Reset Request</div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <!-- Content -->
        <tr>
            <td class="content-padding" style="padding:32px 24px">
                <div style="font-size:20px;font-weight:600;color:#1f2937;margin-bottom:16px">Hi {recipient_name}!</div>
                <p style="margin:0 0 16px 0;font-size:16px;color:#4b5563;line-height:1.6">
                    We received a request to reset your password for your Zuperior account.
                </p>
                <p style="margin:0 0 24px 0;font-size:16px;color:#4b5563;line-height:1.6">
                    Click the button below to reset your password. This link will expire in <strong>1 hour</strong> for security reasons.
                </p>
                
                <!-- CTA Button -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px">
                    <tr>
                        <td style="text-align:center">
                            <a href="{reset_url}" style="display:inline-block;background:linear-gradient(135deg,{BRAND_PRIMARY},{BRAND_PRIMARY_ALT});color:#fff;text-decoration:none;font-weight:600;padding:14px 32px;border-radius:10px;font-size:16px;box-shadow:0 4px 6px rgba(98,66,165,0.3)">
                                Reset Password
                            </a>
                        </td>
                    </tr>
                </table>
                
                <!-- Alternative Link -->
                <div style="background:#f8f9fa;border-radius:8px;padding:16px;margin-bottom:24px">
                    <p style="margin:0 0 8px 0;font-size:12px;color:#6b7280;font-weight:600">Or copy and paste this link:</p>
                    <p style="margin:0;font-size:12px;color:{BRAND_PRIMARY};word-break:break-all">{reset_url}</p>
                </div>
                
                <!-- Security Notice -->
                <div style="background:#fef3c7;border-radius:10px;padding:16px;border-left:4px solid #f59e0b">
                    <p style="margin:0;font-size:14px;color:#78350f;line-height:1.6">
                        <strong>⚠️ Security Notice:</strong><br/>
                        If you didn't request this password reset, please ignore this email. Your password will remain unchanged.<br/>
                        For security reasons, never share this link with anyone.
                    </p>
                </div>
            </td>
        </tr>
        
        <!-- Footer -->
        <tr>
            <td style="background:#fafafa;padding:20px 24px;font-size:12px;color:#6b7280;border-top:1px solid {BORDER_COLOR};border-radius:0 0 16px 16px">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align:center">
                            <p style="margin:0 0 8px 0">© {datetime.now().year} Zuperior. All rights reserved.</p>
                            <p style="margin:0;font-size:11px">This is an automated email. Please do not reply.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''
        
        send_email_to(email, "Reset Your Zuperior Password", text, html)
        logger.info(f"Password reset email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {e}")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = user_crud.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_in.password)
    
    # Create user data
    user_data = user_in.model_dump()
    user_data['password'] = hashed_password
    
    # Create user
    user = user_crud.create(db, obj_in=UserCreate(**user_data))
    
    # Send welcome email in background
    background_tasks.add_task(send_welcome_email_task, user.email, user.name)
    
    return user


@router.post("/login", response_model=Token)
def login(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Login and get access token and refresh token
    """
    # Get user by email
    user = user_crud.get_by_email(db, email=form_data.username)
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != "active":
        status_message = user.status if user.status else "Inactive"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You are {status_message} user and not allowed please contact support."
        )
    
    # Update last login
    user.lastLoginAt = datetime.utcnow()
    db.commit()
    
    # Get device info
    device_info = get_device_info(request)
    
    # Check active sessions count and revoke oldest if needed
    active_sessions = db.query(RefreshToken).filter(
        RefreshToken.userId == user.id,
        RefreshToken.revoked != True,  # Handles None values
        RefreshToken.expiresAt > datetime.utcnow()
    ).order_by(RefreshToken.lastActivity.asc(), RefreshToken.createdAt.asc()).all()
    
    if len(active_sessions) >= settings.MAX_CONCURRENT_SESSIONS:
        # Revoke oldest session
        oldest_session = active_sessions[0]
        oldest_session.revoked = True
        db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.id},
        expires_delta=refresh_token_expires
    )
    
    # Store refresh token in database with device info
    now = datetime.utcnow()
    refresh_token_obj = RefreshToken(
        id=str(uuid.uuid4()),
        userId=user.id,
        token=refresh_token,
        expiresAt=now + refresh_token_expires,
        deviceName=device_info.get("deviceName"),
        ipAddress=device_info.get("ipAddress"),
        userAgent=device_info.get("userAgent"),
        lastActivity=now
    )
    db.add(refresh_token_obj)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/login/json", response_model=Token)
def login_json(
    user_login: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login with JSON body and get access token and refresh token
    """
    # Get user by email
    user = user_crud.get_by_email(db, email=user_login.email)
    
    if not user or not verify_password(user_login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != "active":
        status_message = user.status if user.status else "Inactive"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You are {status_message} user and not allowed please contact support."
        )
    
    # Update last login
    user.lastLoginAt = datetime.utcnow()
    db.commit()
    
    # Get device info (use deviceName from request if provided)
    device_info = get_device_info(request, device_name=user_login.deviceName)
    
    # Check active sessions count and revoke oldest if needed
    active_sessions = db.query(RefreshToken).filter(
        RefreshToken.userId == user.id,
        RefreshToken.revoked != True,  # Handles None values
        RefreshToken.expiresAt > datetime.utcnow()
    ).order_by(RefreshToken.lastActivity.asc(), RefreshToken.createdAt.asc()).all()
    
    if len(active_sessions) >= settings.MAX_CONCURRENT_SESSIONS:
        # Revoke oldest session
        oldest_session = active_sessions[0]
        oldest_session.revoked = True
        db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.id},
        expires_delta=refresh_token_expires
    )
    
    # Store refresh token in database with device info
    now = datetime.utcnow()
    refresh_token_obj = RefreshToken(
        id=str(uuid.uuid4()),
        userId=user.id,
        token=refresh_token,
        expiresAt=now + refresh_token_expires,
        deviceName=device_info.get("deviceName"),
        ipAddress=device_info.get("ipAddress"),
        userAgent=device_info.get("userAgent"),
        lastActivity=now
    )
    db.add(refresh_token_obj)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    token_data: TokenRefresh,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    user = verify_refresh_token(db, token_data.refresh_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get old token to preserve device info
    old_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token
    ).first()
    
    # Get device info (use existing device info from old token if available)
    device_info = get_device_info(request)
    if old_token:
        # Preserve device info from old token, but update IP/user agent if changed
        device_info = {
            "deviceName": old_token.deviceName or device_info.get("deviceName"),
            "ipAddress": device_info.get("ipAddress") or old_token.ipAddress,
            "userAgent": device_info.get("userAgent") or old_token.userAgent
        }
        # Update lastActivity before revoking
        old_token.lastActivity = datetime.utcnow()
        old_token.revoked = True
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    # Create new refresh token
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token = create_refresh_token(
        data={"sub": user.id},
        expires_delta=refresh_token_expires
    )
    
    # Store new refresh token with device info
    now = datetime.utcnow()
    new_token_obj = RefreshToken(
        id=str(uuid.uuid4()),
        userId=user.id,
        token=new_refresh_token,
        expiresAt=now + refresh_token_expires,
        deviceName=device_info.get("deviceName"),
        ipAddress=device_info.get("ipAddress"),
        userAgent=device_info.get("userAgent"),
        lastActivity=now
    )
    db.add(new_token_obj)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    token_data: TokenRefresh,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout and revoke refresh token
    """
    # Revoke the refresh token
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token,
        RefreshToken.userId == current_user.id
    ).first()
    
    if refresh_token:
        # Update lastActivity before revoking
        refresh_token.lastActivity = datetime.utcnow()
        refresh_token.revoked = True
        db.commit()
    
    return {"message": "Successfully logged out"}


@router.post("/logout-all", response_model=LogoutAllResponse, status_code=status.HTTP_200_OK)
def logout_all_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout from all devices by revoking all refresh tokens for the current user
    """
    try:
        now = datetime.utcnow()
        
        # Get all non-revoked, non-expired refresh tokens for the user
        # Use != True to handle None values properly
        active_tokens = db.query(RefreshToken).filter(
            RefreshToken.userId == current_user.id,
            RefreshToken.revoked != True,  # Handles None values
            RefreshToken.expiresAt > now  # Only active tokens
        ).all()
        
        # Revoke all tokens
        count = 0
        for token in active_tokens:
            token.lastActivity = now
            token.revoked = True
            count += 1
        
        db.commit()
        
        logger.info(f"Revoked {count} refresh tokens for user {current_user.id}")
        
        return {
            "message": "Successfully logged out from all devices",
            "sessions_revoked": count
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error revoking tokens for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout from all devices"
        )


@router.get("/active-sessions", response_model=ActiveSessionsResponse, status_code=status.HTTP_200_OK)
def get_active_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all active (non-revoked, non-expired) sessions for the current user
    Returns list of devices currently logged in
    """
    now = datetime.utcnow()
    
    # Get all non-revoked, non-expired refresh tokens
    active_tokens = db.query(RefreshToken).filter(
        RefreshToken.userId == current_user.id,
        RefreshToken.revoked != True,  # Handles None values
        RefreshToken.expiresAt > now
    ).order_by(RefreshToken.lastActivity.desc()).all()
    
    # Transform to response format
    sessions = []
    for token in active_tokens:
        # Parse device and browser from deviceName
        device = "Desktop"
        browser = "Unknown Browser"
        
        if token.deviceName:
            parts = token.deviceName.split(" - ")
            device = parts[0] if parts else "Desktop"
            browser = parts[1] if len(parts) > 1 else "Unknown Browser"
        elif token.userAgent:
            # Fallback: parse from user agent
            ua = token.userAgent.lower()
            if "mobile" in ua or "android" in ua or "iphone" in ua:
                device = "Mobile"
            elif "tablet" in ua or "ipad" in ua:
                device = "Tablet"
            
            if "chrome" in ua:
                browser = "Chrome"
            elif "firefox" in ua:
                browser = "Firefox"
            elif "safari" in ua and "chrome" not in ua:
                browser = "Safari"
            elif "edge" in ua:
                browser = "Edge"
        
        sessions.append({
            "id": token.id,
            "device": device,
            "browser": browser,
            "ipAddress": token.ipAddress,
            "createdAt": token.createdAt or token.lastActivity,
            "lastActivity": token.lastActivity
        })
    
    return {
        "success": True,
        "data": {
            "sessions": sessions
        },
        "count": len(sessions)
    }


@router.post("/forgot-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def forgot_password(
    request_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset - sends email with reset token
    """
    # Find user by email
    user = user_crud.get_by_email(db, email=request_data.email)
    
    # Always return success message to prevent email enumeration
    # Don't reveal whether the email exists or not
    if user:
        # Generate reset token
        reset_token = generate_password_reset_token()
        reset_token_expires = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        
        # Save token to user
        user.resetToken = reset_token
        user.resetTokenExpires = reset_token_expires
        db.commit()
        
        # Send password reset email in background
        background_tasks.add_task(
            send_password_reset_email_task,
            user.email,
            user.name,
            reset_token
        )
    
    # Always return the same message regardless of whether user exists
    return {
        "message": "If an account with that email exists, a password reset link has been sent."
    }


@router.post("/reset-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def reset_password(
    request_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using the reset token
    """
    # Find user by reset token
    user = db.query(User).filter(
        User.resetToken == request_data.token,
        User.resetTokenExpires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Hash new password
    hashed_password = get_password_hash(request_data.newPassword)
    
    # Update password and clear reset token
    user.password = hashed_password
    user.resetToken = None
    user.resetTokenExpires = None
    db.commit()
    
    logger.info(f"Password reset successful for user {user.email}")
    
    return {
        "message": "Password has been reset successfully. You can now login with your new password."
    }

