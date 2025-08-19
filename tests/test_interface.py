"""
tests/test_interface.py
"""


import pytest
import pandas as pd
import gradio as gr
from src import interface
from src.interface import demo


def test_demo_is_gradio_interface():
    assert isinstance(interface.demo, (gr.Blocks, gr.Interface))

def test_demo_df_structure():

    df = interface.demo_df() 
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert {"SKU", "Name", "Price"}.issubset(df.columns)


def test_mapping_template_roundtrip(tmp_path):
     """Ensure mapping templates can be saved/loaded correctly"""

     mapping = {"Name": "Product Name", "Price": "Retail Price"}
     path = tmp_path / "template.json"
     interface.save_mapping(mapping, path)
     loaded = interface.load_mapping(path)
     assert loaded == mapping

def test_transformer_example():
     """Example transform should apply formatting correctly"""

     row = {"Price": "10"}
     out = interface.apply_transforms(row)
     assert isinstance(out["Price"], str)
     assert out["Price"].startswith("£") or out["Price"].isdigit