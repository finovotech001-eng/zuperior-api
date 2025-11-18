from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import random
import re
import logging
from app.services.email_service import send_email_to
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory OTP storage: {email: {"otp": str, "expires_at": datetime, "verified": bool}}
otp_store: Dict[str, Dict[str, Any]] = {}
OTP_EXPIRY_MINUTES = 10

BRAND_PRIMARY = "#6242a5"
BRAND_PRIMARY_ALT = "#9f8bcf"
BORDER_COLOR = "#e5e7eb"
BG_COLOR = "#f9fafb"

def get_logo_url():
    if settings.EMAIL_LOGO_URL:
        return settings.EMAIL_LOGO_URL
    return f"{settings.CLIENT_URL.rstrip('/')}/logo.png"

class OTPEmailRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class MT5AccountEmailRequest(BaseModel):
    email: EmailStr
    login: str
    account_name: Optional[str] = None
    group: Optional[str] = None
    leverage: Optional[int] = None
    master_password: Optional[str] = None
    investor_password: Optional[str] = None
    name: Optional[str] = None

class DepositEmailRequest(BaseModel):
    email: EmailStr
    account_login: str
    amount: str
    date: Optional[str] = None
    name: Optional[str] = None

class WithdrawalEmailRequest(BaseModel):
    email: EmailStr
    account_login: str
    amount: str
    date: Optional[str] = None
    name: Optional[str] = None

class InternalTransferEmailRequest(BaseModel):
    email: EmailStr
    from_account: str
    to_account: str
    amount: str
    date: Optional[str] = None
    name: Optional[str] = None

class WelcomeEmailRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class EmailResponse(BaseModel):
    success: bool
    message: str

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class OTPVerifyResponse(BaseModel):
    success: bool
    verified: bool
    message: str

@router.post("/send-otp", response_model=EmailResponse)
def send_otp_email(request: OTPEmailRequest):
    try:
        otp = str(random.randint(100000, 999999))
        logo_url = get_logo_url()
        name = request.name or ""
        
        # Store OTP with expiration time (10 minutes from now)
        expires_at = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        otp_store[request.email.lower()] = {
            "otp": otp,
            "expires_at": expires_at,
            "verified": False
        }
        
        text = f"Hi {name},\n\nUse the one-time code below to verify your email address.\n\n{otp}\n\nThis code will expire in 10 minutes.\n\nIf you didn't request this email, you can safely ignore it.\n\n- Team Zuperior\n"
        
        html = f'<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"/></head><body style="margin:0;padding:24px;background:{BG_COLOR};font-family:Arial,sans-serif"><table width="100%" style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:12px"><tr><td style="background:linear-gradient(90deg,{BRAND_PRIMARY},{BRAND_PRIMARY_ALT});padding:16px 20px"><img src="{logo_url}" alt="Zuperior" style="height:28px" /><h1 style="margin:0;font-size:20px;color:#fff">Zuperior</h1></td></tr><tr><td style="padding:24px"><p style="margin:0 0 12px 0">Hi {name},</p><p style="margin:0 0 16px 0">Use the one-time code below to verify your email address.</p><div style="letter-spacing:6px;font-weight:700;font-size:28px;text-align:center;margin:18px 0 8px">{otp}</div><p style="margin:0 0 6px 0;font-size:12px;text-align:center">This code will expire in 10 minutes.</p><div style="margin-top:22px;padding:12px 16px;background:#f8f9fa;border-radius:8px;font-size:12px">If you did not request this email, you can safely ignore it.</div><p style="margin-top:24px;font-size:12px">- Team Zuperior</p></td></tr></table></body></html>'
        
        send_email_to(request.email, "Verify your email • Zuperior", text, html)
        return EmailResponse(success=True, message=f"OTP email sent to {request.email}")
    except Exception as e:
        logger.error(f"Error sending OTP email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")

@router.post("/verify-otp", response_model=OTPVerifyResponse)
def verify_otp(request: OTPVerifyRequest):
    """
    Verify the OTP entered by the user.
    Returns success: true and verified: true if OTP is correct and not expired.
    """
    try:
        email_lower = request.email.lower()
        
        # Check if OTP exists for this email
        if email_lower not in otp_store:
            return OTPVerifyResponse(
                success=False,
                verified=False,
                message="No OTP found for this email. Please request a new OTP."
            )
        
        otp_data = otp_store[email_lower]
        
        # Check if OTP has expired
        if datetime.now() > otp_data["expires_at"]:
            # Remove expired OTP
            del otp_store[email_lower]
            return OTPVerifyResponse(
                success=False,
                verified=False,
                message="OTP has expired. Please request a new OTP."
            )
        
        # Check if OTP has already been verified
        if otp_data["verified"]:
            return OTPVerifyResponse(
                success=False,
                verified=False,
                message="This OTP has already been used. Please request a new OTP."
            )
        
        # Verify OTP
        if otp_data["otp"] == request.otp:
            # Mark as verified and remove from store (one-time use)
            del otp_store[email_lower]
            return OTPVerifyResponse(
                success=True,
                verified=True,
                message="OTP verified successfully."
            )
        else:
            return OTPVerifyResponse(
                success=False,
                verified=False,
                message="Invalid OTP. Please check and try again."
            )
    
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP"
        )

@router.post("/send-mt5-account", response_model=EmailResponse)
def send_mt5_account_email(request: MT5AccountEmailRequest):
    try:
        recipient_name = request.name or 'Trader'
        logo_url = get_logo_url()
        dashboard_url = settings.CLIENT_URL
        
        text = f"Hi {recipient_name},\n\nYour new MT5 trading account has been created successfully.\n\nLogin: {request.login}\n"
        if request.account_name:
            text += f"Account Name: {request.account_name}\n"
        if request.group:
            text += f"Group: {request.group}\n"
        if request.leverage:
            text += f"Leverage: 1:{request.leverage}\n"
        if request.master_password:
            text += f"Master Password: {request.master_password}\n"
        if request.investor_password:
            text += f"Investor Password: {request.investor_password}\n"
        text += "\nYou can now sign in to the MT5 platform and start trading.\n\nBest regards,\nZuperior\n"
        
        html = f'<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"/></head><body style="margin:0;padding:24px;background:{BG_COLOR};font-family:Arial,sans-serif"><table width="100%" style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:16px"><tr><td style="background:linear-gradient(90deg,{BRAND_PRIMARY},{BRAND_PRIMARY_ALT});padding:24px"><img src="{logo_url}" alt="Zuperior" style="height:28px" /><div style="font-size:20px;color:#fff;font-weight:700">Zuperior</div><div style="font-size:13px;color:rgba(255,255,255,0.85)">MT5 Account Created</div></td></tr><tr><td style="padding:24px"><div style="font-size:16px;font-weight:600">Hi {recipient_name},</div><p style="margin:8px 0;font-size:14px">Your new MT5 account has been created successfully.</p></td></tr><tr><td align="center" style="padding:0 24px 28px"><a href="{dashboard_url}" style="display:inline-block;background:{BRAND_PRIMARY};color:#fff;text-decoration:none;font-weight:600;padding:12px 18px;border-radius:10px">Open Dashboard</a></td></tr><tr><td style="background:#fafafa;padding:14px 24px;font-size:12px;border-top:1px solid {BORDER_COLOR}">© {datetime.now().year} Zuperior. All rights reserved</td></tr></table></body></html>'
        
        send_email_to(request.email, "Your MT5 trading account is ready", text, html)
        return EmailResponse(success=True, message=f"MT5 account email sent to {request.email}")
    except Exception as e:
        logger.error(f"Error sending MT5 account email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")

@router.post("/send-deposit", response_model=EmailResponse)
def send_deposit_email(request: DepositEmailRequest):
    try:
        recipient_name = request.name or 'Trader'
        logo_url = get_logo_url()
        dashboard_url = settings.CLIENT_URL
        date_str = request.date or datetime.now().isoformat()
        
        text = f"Hi {recipient_name},\n\nWe have received your deposit request.\n\nAccount: {request.account_login}\nAmount: {request.amount}\nDate: {date_str}\n\nOur team will process your deposit and notify you once completed.\n\nBest regards,\nZuperior\n"
        
        html = f'<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"/></head><body style="margin:0;padding:24px;background:{BG_COLOR};font-family:Arial,sans-serif"><table width="100%" style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:16px"><tr><td style="background:linear-gradient(90deg,{BRAND_PRIMARY},{BRAND_PRIMARY_ALT});padding:24px"><img src="{logo_url}" alt="Zuperior" style="height:28px" /><div style="font-size:20px;color:#fff;font-weight:700">Zuperior</div><div style="font-size:13px;color:rgba(255,255,255,0.85)">Deposit Request Created</div></td></tr><tr><td style="padding:24px"><div style="font-size:16px;font-weight:600">Hi {recipient_name},</div><p style="margin:8px 0;font-size:14px">We have received your deposit request.</p></td></tr><tr><td align="center" style="padding:0 24px 28px"><a href="{dashboard_url}" style="display:inline-block;background:{BRAND_PRIMARY};color:#fff;text-decoration:none;font-weight:600;padding:12px 18px;border-radius:10px">Open Dashboard</a></td></tr><tr><td style="background:#fafafa;padding:14px 24px;font-size:12px;border-top:1px solid {BORDER_COLOR}">© {datetime.now().year} Zuperior. All rights reserved</td></tr></table></body></html>'
        
        send_email_to(request.email, "Deposit Request Created", text, html)
        return EmailResponse(success=True, message=f"Deposit email sent to {request.email}")
    except Exception as e:
        logger.error(f"Error sending deposit email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")

@router.post("/send-withdrawal", response_model=EmailResponse)
def send_withdrawal_email(request: WithdrawalEmailRequest):
    try:
        recipient_name = request.name or 'Trader'
        logo_url = get_logo_url()
        dashboard_url = settings.CLIENT_URL
        date_str = request.date or datetime.now().isoformat()
        
        text = f"Hi {recipient_name},\n\nWe have received your withdrawal request.\n\nAccount: {request.account_login}\nAmount: {request.amount}\nDate: {date_str}\n\nOur team will process your withdrawal and notify you once completed.\n\nBest regards,\nZuperior\n"
        
        html = f'<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"/></head><body style="margin:0;padding:24px;background:{BG_COLOR};font-family:Arial,sans-serif"><table width="100%" style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:16px"><tr><td style="background:linear-gradient(90deg,{BRAND_PRIMARY},{BRAND_PRIMARY_ALT});padding:24px"><img src="{logo_url}" alt="Zuperior" style="height:28px" /><div style="font-size:20px;color:#fff;font-weight:700">Zuperior</div><div style="font-size:13px;color:rgba(255,255,255,0.85)">Withdrawal Request Created</div></td></tr><tr><td style="padding:24px"><div style="font-size:16px;font-weight:600">Hi {recipient_name},</div><p style="margin:8px 0;font-size:14px">We have received your withdrawal request.</p></td></tr><tr><td align="center" style="padding:0 24px 28px"><a href="{dashboard_url}" style="display:inline-block;background:{BRAND_PRIMARY};color:#fff;text-decoration:none;font-weight:600;padding:12px 18px;border-radius:10px">Open Dashboard</a></td></tr><tr><td style="background:#fafafa;padding:14px 24px;font-size:12px;border-top:1px solid {BORDER_COLOR}">© {datetime.now().year} Zuperior. All rights reserved</td></tr></table></body></html>'
        
        send_email_to(request.email, "Withdrawal Request Created", text, html)
        return EmailResponse(success=True, message=f"Withdrawal email sent to {request.email}")
    except Exception as e:
        logger.error(f"Error sending withdrawal email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")

@router.post("/send-internal-transfer", response_model=EmailResponse)
def send_internal_transfer_email(request: InternalTransferEmailRequest):
    try:
        recipient_name = request.name or 'Trader'
        logo_url = get_logo_url()
        dashboard_url = settings.CLIENT_URL
        date_str = request.date or datetime.now().isoformat()
        
        text = f"Hi {recipient_name},\n\nYour internal transfer has been completed successfully.\n\nFrom Account: {request.from_account}\nTo Account: {request.to_account}\nAmount: {request.amount}\nDate: {date_str}\n\nYou can view your updated account balances in your dashboard.\n\nBest regards,\nZuperior\n"
        
        html = f'<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"/></head><body style="margin:0;padding:24px;background:{BG_COLOR};font-family:Arial,sans-serif"><table width="100%" style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:16px"><tr><td style="background:linear-gradient(90deg,{BRAND_PRIMARY},{BRAND_PRIMARY_ALT});padding:24px"><img src="{logo_url}" alt="Zuperior" style="height:28px" /><div style="font-size:20px;color:#fff;font-weight:700">Zuperior</div><div style="font-size:13px;color:rgba(255,255,255,0.85)">Internal Transfer Completed</div></td></tr><tr><td style="padding:24px"><div style="font-size:16px;font-weight:600">Hi {recipient_name},</div><p style="margin:8px 0;font-size:14px">Your internal transfer has been completed successfully.</p></td></tr><tr><td align="center" style="padding:0 24px 28px"><a href="{dashboard_url}" style="display:inline-block;background:{BRAND_PRIMARY};color:#fff;text-decoration:none;font-weight:600;padding:12px 18px;border-radius:10px">Open Dashboard</a></td></tr><tr><td style="background:#fafafa;padding:14px 24px;font-size:12px;border-top:1px solid {BORDER_COLOR}">© {datetime.now().year} Zuperior. All rights reserved</td></tr></table></body></html>'
        
        send_email_to(request.email, "Internal Transfer Completed", text, html)
        return EmailResponse(success=True, message=f"Internal transfer email sent to {request.email}")
    except Exception as e:
        logger.error(f"Error sending internal transfer email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")

@router.post("/send-welcome", response_model=EmailResponse)
def send_welcome_email(request: WelcomeEmailRequest):
    try:
        recipient_name = request.name or 'Trader'
        logo_url = get_logo_url()
        dashboard_url = settings.CLIENT_URL
        
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
        
        send_email_to(request.email, "Welcome to Zuperior! 🎉", text, html)
        return EmailResponse(success=True, message=f"Welcome email sent to {request.email}")
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")


class CustomEmailAttachment(BaseModel):
    filename: str
    content: str  # Base64 encoded content
    content_type: Optional[str] = "application/octet-stream"


class CustomEmailRequest(BaseModel):
    recipient_email: EmailStr
    subject: str
    content_body: str  # HTML or plain text content
    is_html: Optional[bool] = True  # Whether content_body is HTML or plain text
    attachments: Optional[List[CustomEmailAttachment]] = None


@router.post("/send-custom", response_model=EmailResponse)
def send_custom_email(request: CustomEmailRequest):
    """
    Send a custom email with optional attachments
    
    - **recipient_email**: Email address of the recipient
    - **subject**: Email subject line
    - **content_body**: Email body content (HTML or plain text)
    - **is_html**: Whether content_body is HTML (default: True) or plain text
    - **attachments**: Optional list of file attachments (base64 encoded)
    """
    try:
        # Prepare text and HTML versions
        if request.is_html:
            html = request.content_body
            # Create a simple plain text version from HTML (basic conversion)
            # Remove HTML tags for plain text version
            text = re.sub(r'<[^>]+>', '', html)
            text = text.strip() or "Please view this email in an HTML-enabled email client."
        else:
            text = request.content_body
            # Create a simple HTML version from plain text
            html = f'<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;"><pre style="white-space: pre-wrap;">{request.content_body}</pre></body></html>'
        
        # Convert attachments to the format expected by send_email_to
        attachments = None
        if request.attachments:
            attachments = []
            for att in request.attachments:
                attachments.append({
                    'filename': att.filename,
                    'content': att.content,  # Already base64 encoded string
                    'content_type': att.content_type
                })
        
        send_email_to(
            to=request.recipient_email,
            subject=request.subject,
            text=text,
            html=html,
            attachments=attachments
        )
        
        return EmailResponse(
            success=True, 
            message=f"Custom email sent to {request.recipient_email}"
        )
    except Exception as e:
        logger.error(f"Error sending custom email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to send email: {str(e)}"
        )
