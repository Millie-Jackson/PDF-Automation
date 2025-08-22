"""
src/csvbot/validate.py
"""


from __future__ import annotations
import pandas as pd
from typing import List


def validate_schema(df: pd.DataFrame, required: List[str]) -> dict:

    missing = [c for c in required if c not in df.columns]

    return {"missing_columns": missing, "ok": len(missing) == 0}