"""
src/sender.py
"""


import smtplib
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


def send_pdf_via_email(pdf_path, subject="Your PDF from Nested{Loop}", body=None):

    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content("Your PDF from Nested{Loop}")

    # Attach PDF
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
        msg.add_attachment(pdf_data, maintype="application", subtype="pdf", filename=os.path.basename(pdf_path))

    # Connect to Email SMTP
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
            print(f"Email sent to {EMAIL_TO}")
    except Exception as e:
        print(f"Failed to send email: {e}")
