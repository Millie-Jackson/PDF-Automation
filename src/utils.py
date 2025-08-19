"""
src/utils.py
"""


import json
import pandas as pd
from pathlib import Path
from typing import Union


PathLike = Union[str, Path]


def save_mapping(mapping: dict, path: Path):
    """Save a column mapping template to JSON."""

    path = Path(path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)

def load_mapping(path: Path) -> dict:
    """Load a column mapping template from JSON."""

    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def apply_transforms(row: dict) -> dict:
    """Apply transformations to a row of data.
    Example: format prices, pad IDs, etc.
    """

    out = dict(row)

    # Example: ensure Price is a string with currency
    if "Price" in out and isinstance(out["Price"], (int, float, str)):
        try:
            price = float(out["Price"])
            out["Price"] = f"£{price:.2f}"
        except ValueError:
            pass

    return out

def demo_df() -> pd.DataFrame:
    """Return a demo dataframe to show in Gradio."""

    data = [
        {"SKU": "12345", "Name": "Banana Slicer", "Price": 9.99},
        {"SKU": "67890", "Name": "Haunted Toaster", "Price": 49.50},
    ]

    df = pd.DataFrame(data)
    
    return df