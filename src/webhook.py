"""
src/webhook.py
"""


import requests
from datetime import datetime
import os
from typing import Tuple


DEMO_MODE = os.getenv("DEMO_MODE", "1") == "1" or bool(os.getenv("SPACE_ID"))


def post_webhook_message(webhook_url: str | None, pdf_path: str,payload_extra: dict | None = None) -> Tuple[bool, str]:
    
    if DEMO_MODE:
        msg = f"[DEMO] Webhook called with {os.path.basename(pdf_path)}"
        print(msg)
        return True, msg

    if not webhook_url:
        return False, "No webhook URL provided."
    payload = {"file": os.path.basename(pdf_path)}

    if payload_extra:
        payload.update(payload_extra)

    try:
        r = requests.post(webhook_url, json=payload, timeout=8)
        if r.status_code // 100 == 2:
            return True, "Webhook posted."
        return False, f"Webhook error: {r.status_code} {r.text}"
    except Exception as e:
        return False, f"Webhook failed: {e}"         