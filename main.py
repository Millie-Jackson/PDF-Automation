"""
src/main.py
"""


import pandas as pd
from src.excel_parser import load_excel, validate_columns, clean_dataframe, add_computed_fields
from src.pdf_generator import ProductSheetPDF


df = load_excel("data/sample_products.xlsx")
validate_columns(df)
df = clean_dataframe(df)
df = add_computed_fields(df)

pdf = ProductSheetPDF()
pdf.cover_page("Product Sheet")
pdf.add_page()

stripe_toggle = False

for _, row in df.iterrows():
    if pdf.get_y() > 260:
        pdf.add_page()
    pdf.add_product_block(row, stripe=stripe_toggle)
    stripe_toggle = not stripe_toggle

pdf.output("outputs/product_sheet.pdf")
