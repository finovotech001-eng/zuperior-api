import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import logging
from typing import Optional, List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

def send_email_to(to: str, subject: str, text: str, html: str, attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
    """
    Send email using SMTP with optional attachments
    
    Args:
        to: Recipient email address
        subject: Email subject
        text: Plain text body
        html: HTML body
        attachments: Optional list of attachment dicts with keys:
            - filename: str (required)
            - content: bytes or str (required) - file content
            - content_type: str (optional) - MIME type, defaults to 'application/octet-stream'
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = settings.SMTP_FROM
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                filename = attachment.get('filename')
                content = attachment.get('content')
                content_type = attachment.get('content_type', 'application/octet-stream')
                
                if not filename or content is None:
                    logger.warning(f'Skipping invalid attachment: missing filename or content')
                    continue
                
                # Handle base64 encoded content
                if isinstance(content, str):
                    try:
                        # Try to decode base64 string
                        content = base64.b64decode(content)
                    except Exception:
                        # If not base64, treat as plain text
                        content = content.encode('utf-8')
                elif not isinstance(content, bytes):
                    content = str(content).encode('utf-8')
                
                # Create attachment
                part = MIMEBase(*content_type.split('/', 1))
                part.set_payload(content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(part)
        
        # Use SMTP_SSL if SMTP_SECURE is True, otherwise use STARTTLS
        if settings.SMTP_SECURE:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg)
        
        logger.info(f'Email sent to {to} with {len(attachments) if attachments else 0} attachment(s)')
        return True
    except Exception as e:
        logger.error(f'Failed to send email: {e}')
        raise
