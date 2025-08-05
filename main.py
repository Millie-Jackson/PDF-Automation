"""
src/main.py

Main CLI script for PDF generation.
Supports both single file and folder batch processing.
"""


import argparse
from src.run_generators import generate_pdf_from_excel, generate_pdfs_from_folder
from src.watcher import start_watching
from src.sender import send_pdf_via_email
from src.scheduler import start_scheduler
from dotenv import load_dotenv


load_dotenv()


def main():

    parser = argparse.ArgumentParser(description="Generate PDF product sheets from Excel")
    parser.add_argument('--file', type=str, help="Path to a single Excel file to convert")
    parser.add_argument('--folder', type=str, help="Path to a folder containing multiple Excel files")
    parser.add_argument('--watch', action='store_true', help="Watch the folder for file changes")
    parser.add_argument('--email', type=str, help="Path to PDF to send via email")
    parser.add_argument('--schedule', action='store_true', help="Start email scheduler")

    args = parser.parse_args()

    if args.file:
        output_path = "outputs/" + args.file.split("/")[-1].replace(".xlsx", ".pdf")
        generate_pdf_from_excel(args.file, output_path)
    elif args.folder:
        generate_pdfs_from_folder(input_folder=args.folder, output_folder="outputs")
    elif args.watch:
        start_watching()
    elif args.email:
        send_pdf_via_email(args.email)
    elif args.schedule:
        start_scheduler()
    else:
        print("Please provide either --file, --folder or --watch")

    
if __name__ == "__main__":
    main()
