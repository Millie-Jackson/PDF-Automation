"""
src/main.py

Main CLI script for PDF generation.
Supports both single file and folder batch processing.
"""


import argparse
import os
from src.run_generators import generate_pdf_from_excel, generate_pdfs_from_folder
from src.watcher import start_watcher
from src.sender import send_pdf_via_email
from src.scheduler import start_scheduler
from src.slack import post_to_slack
from src.webhook import post_webhook_message
from dotenv import load_dotenv


load_dotenv()


def main():

    parser = argparse.ArgumentParser(description="PDF Automation Toolkit - Nested{Loop}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommands
    generate = subparsers.add_parser("generate", help="Generate PDF from file or folder")
    generate.add_argument("--input", type=str, help="Path to Excel file")
    generate.add_argument("--folder", type=str, help="Folder of Excel files")
    generate.add_argument("--output", type=str, help="Path to save PDF (for single file only)")
    generate.add_argument("--email", action="store_true", help="Send email after generating")
    generate.add_argument("--slack", action="store_true", help="Post to Slack after generating")
    generate.add_argument("--webhook", action="store_true", help="Send webhook after generating")

    # Schedule subcommand
    subparsers.add_parser("schedule", help="Run email scheduler for new/summary PDFs")

    # Watch subcommand
    subparsers.add_parser("watch", help="Watch folder for new Excel files and auto-generate PDFs")

    args = parser.parse_args()

    if args.command == "generate":
        if args.input:
            output_path = args.output or "outputs/generated_output.pdf"
            generate_pdf_from_excel(args.input, output_path)
            if args.email:
                send_pdf_via_email(output_path)
            if args.slack:
                post_to_slack(output_path)
            if args.webhook:
                post_webhook_message(os.getenv("WEBHOOK_URL"), output_path)
        elif args.folder:
            generate_pdfs_from_folder(args.folder)
        else:
            print("You must provide --input or --folder")

    elif args.command == "schedule":
        start_scheduler()

    elif args.command == "watch":
        start_watcher()

    
if __name__ == "__main__":
    main()
