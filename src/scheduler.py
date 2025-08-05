"""
src/scheduler.py
"""


import os
import schedule
import time
from datetime import datetime
from email.message import EmailMessage
from src.sender import send_pdf_via_email, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO
from dotenv import load_dotenv


load_dotenv()

OUTPUT_FOLDER = "outputs"
SENT_LOG_FILE = os.getenv("SENT_LOG_FILE", "outputs/sent_files.txt")


def load_sent_files():

    if not os.path.exists(SENT_LOG_FILE):
        return set()
    
    with open(SENT_LOG_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_sent_file(filename):

    with open(SENT_LOG_FILE, "a") as f:
        f.write(filename + "\n")

def send_unsent_pdfs():

    sent_files = load_sent_files()
    for file in os.listdir(OUTPUT_FOLDER):
        if file.endswith(".pdf") and file not in sent_files:
            path = os.path.join(OUTPUT_FOLDER, file)
            send_pdf_via_email(
                pdf_path=path,
                subject=f"[Nested{{Loop}}] New PDF: {file}",
                body=f"Here's yor freshly generated production sheet: {file}"
            )
            save_sent_file(file)

def send_monthly_summary():

    all_pdfs = [
        os.path.join(OUTPUT_FOLDER, f)
        for f in os.listdir(OUTPUT_FOLDER)
        if f.endswith(".pdf")
    ]

    if not all_pdfs:
        print("No PDFs to include in summary.")
        return
    
    msg_body = f"""Hello from Nested{{Loop}} 👋

    Here’s your monthly summary of product sheets. 
    Attached are {len(all_pdfs)} files from the past month.

    Best,
    Your Automation System
    """
    msg = EmailMessage()
    msg["Subject"] = "[Nested{Loop}] Monthly Summary – Product Sheets"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content(msg_body)

    for pdf in all_pdfs:
        send_pdf_via_email(
            pdf_path=pdf,
            subject="[Nested{Loop}] Monthly Summary - Project Sheet",
            body=f"This is your monthly archive of : {os.path.basename(pdf)}"
        )

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
            print(f"Monthly summary email sent with {len(all_pdfs)} attachments.")
    except Exception as e:
        print(f"Failed to send summary: {e}")

def start_scheduler(run_for_minutes=6):

    print("Scheduler started!")
    start_time = time.time()

    # Every 2 mins - simlated instant-on-change delivery
    schedule.every(2).minutes.do(send_unsent_pdfs)

    # For real monthly schedule use:
    # schedule.every().month.at("09:00").do(send_monthly_summary)

    # Simulate monthly summary every 5 minutes (for testing)
    schedule.every(5).minutes.do(send_monthly_summary)

    while True:
        schedule.run_pending()
        time.sleep(1)

        # Auto-exit after time limit
        elapsed = (time.time() - start_time) / 60
        if elapsed > run_for_minutes:
            print("Scheduler finished - time limit reached.")
            break