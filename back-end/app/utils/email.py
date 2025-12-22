import smtplib
from email.message import EmailMessage
from typing import Optional

from app.core.config import settings


def send_reset_email(to_email: str, reset_link: str, subject: Optional[str] = "Password reset"):
    """Send a simple reset email using SMTP settings from `settings`.
    This is a minimal, synchronous implementation intended for BackgroundTasks.
    In production use a transactional email provider (SendGrid, SES, etc.)."""

    smtp_host = getattr(settings, "SMTP_HOST", None)
    smtp_port = getattr(settings, "SMTP_PORT", None)
    smtp_user = getattr(settings, "SMTP_USER", None)
    smtp_pass = getattr(settings, "SMTP_PASSWORD", None)
    email_from = getattr(settings, "EMAIL_FROM", None) or smtp_user

    if not smtp_host or not smtp_port:
        # SMTP not configured; log and return
        print("SMTP not configured, skipping email send")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = to_email
    msg.set_content(f"You requested a password reset. Click the link to reset your password:\n\n{reset_link}\n\nIf you didn't request this, ignore this email.")

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception as e:
        # In production, use logging instead of print
        print(f"Failed to send email to {to_email}: {e}")