"""
src/csvbot/lookup.py
"""


from __future__ import annotations
from pathlib import Path
import pandas as pd
from typing import Dict


class DatabaseLookups:

    def __init__(self):
        self._cache: Dict[str, Dict[ str, str]] = {}

    
    def get_map(self, file: str | Path, key: str, value: str) -> Dict[str, str]:

        fid = f"{Path(file).resolve()}::{key}->{value}"
        if fid in self._cache:
            return self._cache[fid]
        
        df = pd.read_csv(file, dtype=str, keep_default_na=False)

        # Remove white space form header and cell values
        df.columns = [c.strip() for c in df.columns]
        key = key.strip()
        value = value.strip()
        if key not in df.columns or value not in df.columns:
            raise KeyError(f"Lookup file {file} missing columns {key}/{value}")
        
        # Trim keys and values before building
        keys = df[key].astype(str).str.strip()
        vals = df[value].astype(str).str.strip()
        mapping = dict(zip(keys, vals))
        self._cache[fid] = mapping
        
        return mapping