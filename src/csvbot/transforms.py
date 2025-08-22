"""
src/csvbot/transorms.py
"""


from __future__ import annotations
import re


def _s(x) -> str: return "" if x is None else str(x)
def trim(x): return _s(x).strip()
def upper(x): return _s(x).upper()
def lower(x): return _s(x).lower()
def digits_only(x): return re.sub(r"[^0-9]", "", _s(x))


def currency_to_minor(x):
    """12.34"->"1234"; "12"->"1200"; strip symbols and commas"""

    s = re.sub(r"[^0-9.,-]", "", _s(x)).replace(",", "")
    if not s:
        return "" 
    if "." in s:
        pounds, pennies = (s.split(".", 1) + ["0"])[:2]
        pennies = (pennies + "00")[:2]
        return f"{pounds}{pennies}"
    return f"{s}00"


BUILTINS = {
    "trim": trim,
    "upper": upper,
    "lower": lower,
    "digits_only": digits_only,
    "currency_to_minor": currency_to_minor,
}