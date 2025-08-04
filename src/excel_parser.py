"""
src/excel_parser.py
"""


import pandas as pd


REQUIRED_COLUMNS = {"SKU", "Name", "Description", "Price"}


def validate_columns(df):
    
    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing: 
        raise ValueError(f"Missing required columns: {missing}")

def clean_empty_rows(df):

    return df.dropna(how='all')

def check_for_invalid_values(df):

    if df["Price"].isnull().any():
        print("Warning: Some products have no price.")
    
    if (df["Price"] < 0).any():
        print("Warning: Negative price found.")

def load_excel(path):
    """Load Excel file and return a DataFrame."""

    try:
        df = pd.read_excel(path, engine='openpyxl')
        return df
    except Exception as e:
        raise ValueError(f"Failed to load Excel: {e}")
    
def load_all_sheets(path):
    """Load all sheets as a dict of DataFrames."""

    try:
        sheets = pd.read_excel(path, sheet_name=None, engine='openpyxl')
        return sheets # dict: {sheet_name: DataFrame}
    except Exception as e:
        raise ValueError(f"Failed to load multiple sheets: {e}")