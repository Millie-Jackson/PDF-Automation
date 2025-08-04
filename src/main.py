"""
src/main.py
"""


from excel_parser import load_excel, validate_columns, clean_dataframe, add_computed_fields


df = load_excel("data/sample_products.xlsx")
validate_columns(df)
df = clean_dataframe(df)
df = add_computed_fields(df)

print(df.head())