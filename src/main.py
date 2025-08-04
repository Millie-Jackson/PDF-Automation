"""
src/main.py
"""


from excel_parser import load_excel, validate_columns


df = load_excel("data/sample_products.xlsx")
validate_columns(df)

print(df.head())