"""
src/run_generator.py
"""


import os
from src.excel_parser import load_excel, validate_columns, clean_dataframe, add_computed_fields
from src.pdf_generator import ProductSheetPDF

def generate_pdf_from_excel(excel_path, output_path):
    """
    Generate a PDF from a single Excel file with branding, formatting, and styling.

    Parameters:
        excel_path (str): Path to the Excel (.xlsx) file.
        output_path (str): Output path for the generated PDF.
        title (str): Title for the PDF cover page.
    """

    try:
        # Load & clean data
        df = load_excel(excel_path)
        validate_columns(df)
        df = clean_dataframe(df)
        df = add_computed_fields(df)

        # Set up PDF
        pdf = ProductSheetPDF()
        pdf.cover_page("Product Sheet")
        pdf.add_page()

        stripe_toggle = False
        for _, row in df.iterrows():
            if pdf.get_y() > 260:
                pdf.add_page()
            pdf.add_product_block(row, stripe=stripe_toggle)
            stripe_toggle = not stripe_toggle

        # Save to file
        pdf.output(output_path)
        print(f"Generated: {output_path}")

    except Exception as e:
        print(f"Failed to process {excel_path}: {e}")

def generate_pdfs_from_folder(input_folder: str = "data", output_folder: str = "outputs") -> None:
    """
    Generate PDFs from all Excel files in a folder.

    Parameters:
        input_folder (str): Directory containing Excel files.
        output_folder (str): Directory to save generated PDFs.
    """

    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".xlsx"):
            excel_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_folder, f"{base_name}.pdf")
            generate_pdf_from_excel(excel_path, output_path)