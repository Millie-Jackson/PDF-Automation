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
pdf.add_page()

for _, row in df.iterrows():
    if pdf.get_y() > 260:
        pdf.add_page()
    pdf.add_product_block(row)

pdf.output("outputs/product_sheet.pdf")
