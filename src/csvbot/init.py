"""
src/csvbot/init.py
"""


from .io import read_csv_any, write_csv
from .templates import Template, TemplateRegistry
from .lookup import DatabaseLookups
from .mapper import apply_template