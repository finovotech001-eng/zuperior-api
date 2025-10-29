from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import random
import logging
from app.services.email_service import send_email_to
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

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

class EmailResponse(BaseModel):
    success: bool
    message: str

@router.post("/send-otp", response_model=EmailResponse)
def send_otp_email(request: OTPEmailRequest):
    try:
        otp = str(random.randint(100000, 999999))
        logo_url = get_logo_url()
        name = request.name or ""
        
        text = f"Hi {name},\n\nUse the one-time code below to verify your email address.\n\n{otp}\n\nThis code will expire in 10 minutes.\n\nIf you didn't request this email, you can safely ignore it.\n\n- Team Zuperior\n"
        
        html = f'<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"/></head><body style="margin:0;padding:24px;background:{BG_COLOR};font-family:Arial,sans-serif"><table width="100%" style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:12px"><tr><td style="background:linear-gradient(90deg,{BRAND_PRIMARY},{BRAND_PRIMARY_ALT});padding:16px 20px"><img src="{logo_url}" alt="Zuperior" style="height:28px" /><h1 style="margin:0;font-size:20px;color:#fff">Zuperior</h1></td></tr><tr><td style="padding:24px"><p style="margin:0 0 12px 0">Hi {name},</p><p style="margin:0 0 16px 0">Use the one-time code below to verify your email address.</p><div style="letter-spacing:6px;font-weight:700;font-size:28px;text-align:center;margin:18px 0 8px">{otp}</div><p style="margin:0 0 6px 0;font-size:12px;text-align:center">This code will expire in 10 minutes.</p><div style="margin-top:22px;padding:12px 16px;background:#f8f9fa;border-radius:8px;font-size:12px">If you did not request this email, you can safely ignore it.</div><p style="margin-top:24px;font-size:12px">- Team Zuperior</p></td></tr></table></body></html>'
        
        send_email_to(request.email, "Verify your email • Zuperior", text, html)
        return EmailResponse(success=True, message=f"OTP email sent to {request.email}")
    except Exception as e:
        logger.error(f"Error sending OTP email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")

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
