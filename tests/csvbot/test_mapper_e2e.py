"""
test/csvbot/test_mapper_e2e.py
"""


import pandas as pd
from pathlib import Path
from src.csvbot.templates import Template
from src.csvbot.lookup import DatabaseLookups
from src.csvbot.mapper import apply_template


def test_apply_template(tmp_path: Path):

    df = pd.DataFrame({"ID":["001"], "SKU":["abc"], "QTY":["10"], "PRICE":["1.23"], "CUST_ID":["X"]})
    lk = tmp_path / "lk.csv"
    lk.write_text("CUST_ID, SEGMENT\nX, VIP\n")
    t = Template(
        name="t", version=1,
        output_schema=["id", "sku", "qty", "price_pennies", "segment"],
        mapping={
            "id":{"from":"ID","transforms":["trim"]},
            "sku":{"from":"SKU","transforms":["upper"]},
            "qty":{"from":"QTY","transforms":["digits_only"]},
            "price_pennies":{"from":"PRICE","transforms":["currency_to_minor"]},
            "segment":{"lookup":{"file": str(lk), "key":"CUST_ID", "value":"SEGMENT"}},
        },
        constants={}, missing={"policy":"fill", "value": ""}
    )

    out = apply_template(df, t, DatabaseLookups())
    assert out.to_dict(orient="records")[0] == {"id":"001","sku":"ABC","qty":"10","price_pennies":"123","segment":"VIP"}
