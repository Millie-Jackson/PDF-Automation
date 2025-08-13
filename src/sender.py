"""
src/sender.py
"""


import smtplib, ssl, mimetypes
import os
from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()

SMTP_HOST = os.getenv("MAILTRAP_HOST")
SMTP_PORT = int(os.getenv("MAILTRAP_PORT", 587))
SMTP_USER = os.getenv("MAILTRAP_USER")
SMTP_PASS = os.getenv("MAILTRAP_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")

# Demo by default on Spaces; set DEMO_MODE=0 locally for real sends
DEMO_MODE = os.getenv("DEMO_MODE", "1") == "1" or bool(os.getenv("SPACE_ID"))


def _get_env(name: str, fallback: str | None = None) -> str | None:
    
    # Allow both MAILTRAP_* and SMTP_* naming
    val = os.getenv(name)
    if val is not None:
        return val
   
    # If name like SMTP_HOST, try MAILTRAP_HOST as fallback
    if name.startswith("SMTP_"):
        mt = "MAILTRAP_" + name[len("SMTP_") :]
        return os.getenv(mt, fallback)
    
    return fallback

def send_pdf_via_email(pdf_path, to_email: str | None = None, subject="Your PDF from Nested{Loop}", body: str | None = None):

    if DEMO_MODE:
        msg = f"[Demo] Email 'sent' to {to_email or 'demo@nestedloop.ai'} with attachment: {os.path.basename(pdf_path)}"
        print(msg)
        return True, msg
    
    # Read credentials (supports either SMTP_* or MAILTRAP_* env vars)
    smtp_host = _get_env("SMTP_HOST")
    smtp_port = int(_get_env("SMTP_PORT", "587") or "587")
    smtp_user = _get_env("SMTP_USER")
    smtp_pass = _get_env("SMTP_PASS")
    from_email = _get_env("FROM_EMAIL") or smtp_user
    to_email = to_email or _get_env("TO_EMAIL") or smtp_user

    if not all([smtp_host, smtp_user, smtp_pass, from_email, to_email]):
        return False, "Missing SMTP credentials/env vars (SMTP_* or MAILTRAP_*)."

    if not os.path.exists(pdf_path):
        return False, f"Attachment not found: {pdf_path}"
    
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject or "Product Sheet"
    msg.set_content(body or "Attached: generated product sheet.")

    ctype, _ = mimetypes.guess_type(pdf_path)
    ctype = ctype or "application/pdf"

    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype=ctype.split("/")[0], subtype=ctype.split("/")[1], filename=os.path.basename(pdf_path))

    try:
        if smtp_port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=10) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.ehlo()
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        return True, "Email sent."
    except Exception as e:
        return False, f"Email failed: {e}"
