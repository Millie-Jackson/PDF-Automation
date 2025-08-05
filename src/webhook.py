"""
src/webhook.py
"""


import requests
from datetime import datetime
import os


def post_webhook_message(url: str, filename: str):

    if not os.path.exists(filename):
        print(f"[Webhook] File not found: {filename}")
        return
    
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "text": f"New file available: '{os.path.basename}(filename)'\n {time_str}"

    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"[Webhook] Posted '{filename}' successfully")
        else:
            print(f"[Webhook] Failed with status: {response.status_code}")
    except Exception as e:
        print(f"[Webhook] Error posting: {e}")            