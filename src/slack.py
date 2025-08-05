"""
src/slack.py
"""


from datetime import datetime
import os


def post_to_slack(pdf_path, channel="#Product-updates"):

    if not os.path.exists(pdf_path):
        print(f"[Slack] File not found: {pdf_path}")
        return
    
    timestamp = datetime.now().strftime("%H:%M")
    filename = os.path.basename(pdf_path)
    print(f"[Slack] Posted '{filename}' to {channel} at {timestamp}")