"""
tests/test_utils.py
"""


import json
from pathlib import Path
import pandas as pd
from src.utils import save_mapping, load_mapping, apply_transforms, demo_df

def test_demo_df_structure():
    df = demo_df()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert {"SKU", "Name", "Price"}.issubset(df.columns)

def test_save_and_load_mapping(tmp_path: Path):
    mapping = {"Name": "Product Name", "Price": "Retail Price"}
    p = tmp_path / "template.json"
    save_mapping(mapping, p)
    loaded = load_mapping(p)
    assert loaded == mapping

def test_apply_transforms_currency():
    row = {"Price": "10"}
    out = apply_transforms(row)
    assert isinstance(out["Price"], str)
    assert out["Price"].startswith("£")
    assert out["Price"].endswith("10.00")