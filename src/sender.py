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


def send_pdf_via_email(pdf_path, to_email: str | None = None, subject="Your PDF from Nested{Loop}", body: str | None = None):

    if DEMO_MODE:
        msg = f"[Demo] Email 'sent' to {to_email or 'demo@nestedloop.ai'} with attachment: {os.path.basename(pdf_path)}"
        print(msg)
        return True, msg
    
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMPT_PORT", "465"))
    smpt_user = os.getenv("SMPT_USER")
    smpt_pass = os.getenv("SMPT_PASS")
    from_email = os.getenv("FROM_EMAIL", smpt_user)
    to_email = to_email or os.getenv("TO_EMAIL", smpt_user)

    if not all([smtp_host, smpt_user, smpt_pass, from_email, to_email]):
        return False, "Missing SMTP credentials/env vars."
    
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
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=10) as server:
            server.login(smpt_user, smpt_pass)
            server.send_message(msg)
        return True, "Email sent."
    except Exception as e:
        return False, f"Email failed: {e}"
