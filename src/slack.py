"""
src/slack.py
"""


from datetime import datetime
import os


DEMO_MODE = os.getenv("DEMO_MODE", "1") == "1" or bool(os.getenv("SPACE_ID"))


def post_to_slack(pdf_path: str, channel: str | None = None, text: str | None = None):

    if DEMO_MODE:
        msg = f"[DEMO] Slack post to {channel or '#product-updates'} with file: {os.path.basename(pdf_path)}"
        print(msg)
        return True, msg

    # (Optional real webhook/file-upload if DEMO_MODE=0)
    import requests
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return False, "Missing SLACK_WEBHOOK_URL."
    payload = {"text": text or f"New PDF: {os.path.basename(pdf_path)}"}
    try:
        r = requests.post(webhook_url, json=payload, timeout=8)
        if r.status_code // 100 == 2:
            return True, "Slack message posted."
        return False, f"Slack error: {r.status_code} {r.text}"
    except Exception as e:
        return False, f"Slack failed: {e}"