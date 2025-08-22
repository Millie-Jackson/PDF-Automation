"""
src/csvbot/io.py
"""


from pathlib import Path
import pandas as pd
import csv


READ_KW = dict(dtype=str, keep_default_na=False, na_filter=False)


def read_csv_any(path: str | Path) -> pd.DataFrame:

    p = Path(path)

    try: 
        return pd.read_csv(p, encoding="utf-8", **READ_KW)
    except UnicodeDecoderError:
        return pd.read_csv(p, encoding="latin1", **READ_KW)
    
def write_csv(df: pd.DataFrame, path: str | Path, quote_all: bool = True) -> None:

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    # stringify to protect long numbers
    df = df.applymap(lambda x: "" if x is None or (isinstance(x, float) and pd.isna(x)) else str(x))
    quoting = csv.QUOTE_ALL if quote_all else csv.QUOTE_MINIMAL
    df.to_csv(p, index=False, quoting=quoting, encoding="utf-8", lineterminator="\n")