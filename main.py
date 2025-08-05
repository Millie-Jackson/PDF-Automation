"""
src/main.py

Main CLI script for PDF generation.
Supports both single file and folder batch processing.
"""


import argparse
from src.run_generators import generate_pdf_from_excel, generate_pdfs_from_folder

def main():

    parser = argparse.ArgumentParser(description="Generate PDF product sheets from Excel")
    parser.add_argument('--file', type=str, help="Path to a single Excel file to convert")
    parser.add_argument('--folder', type=str, help="Path to a folder containing multiple Excel files")

    args = parser.parse_args()

    if args.file:
        output_path = "outputs/" + args.file.split("/")[-1].replace(".xlsx", ".pdf")
        generate_pdf_from_excel(args.file, output_path)
    elif args.folder:
        generate_pdfs_from_folder(input_folder=args.folder, output_folder="outputs")
    else:
        print("Please provide either --file or --foler")

    
if __name__ == "__main__":
    main()
