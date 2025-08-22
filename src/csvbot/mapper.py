"""
src/csvbot/mapper.py
"""


from __future__ import annotations
import pandas as pd
from typing import Any
from .transforms import BUILTINS
from .lookup import DatabaseLookups


def apply_template(df: pd.DataFrame, template, lookups: DatabaseLookups) -> pd.DataFrame:

    out_cols = template.output_schema
    out = pd.DataFrame(columns=out_cols)

    for col in out_cols:
        spec: dict[str, Any] | None = template.mapping.get(col)
        if not spec:
            out[col] = template.constants.get(col, template.missing.get("value", ""))
            continue

        # Base series
        if "from" in spec:
            src_col = spec["from"]
            if src_col in df.columns:
                series = df[src_col]
            else:
                series = pd.Series([""] * len(df), index=df.index)
        else: 
            series = pd.Series([""] * len(df), index=df.index)

        # Ensure string dtype before transorms
        series = series.astype(str)

        # Transforms
        for t in spec.get("transforms", []):
            fn = BUILTINS.get(t)
            if fn is None:
                raise ValueError(f"Unknown transform: {t}")
            series = series.map(fn)

        # Lookup (overrides series with lookup result by key)
        if "lookup" in spec:
            lk = spec["lookup"]
            mp = lookups.get_map(lk["file"], lk["key"], lk["value"])
            key_series = df.get(lk["key"], "").astype(str)
            series = key_series.map(mp).fillna("").astype(str)

        out[col] = series.astype(str)

    if template.missing.get("policy") == "fill":
        out = out.fillna(template.missing.get("value", ""))
    return out
