"""
src/csv/editor.py

Helpers for creating, validating, summarizing, and saving mapping templates.

These functions back the Template Editor tab. They keep file I/O and YAML parsing
out of the UI code so it’s easier to test.
"""


from __future__ import annotations
from pathlib import Path
import re, yaml, pandas as pd
from .transforms import BUILTINS


# Where templates are stored in the repo (and on Spaces if the dir is writable)
TEMPLATE_DIR = Path("templates/csv")


def slugify(name: str) -> str:
    """
    Convert a free-form template name into a safe filename slug.

    Examples:
        "My Cool Template!" -> "my-cool-template"
        "  spaces__and #! punctuation " -> "spaces-and-punctuation"
    """

    s = re.sub(r"[^a-z0-9\-]+", "-", name.lower().strip())
    s = re.sub(r"-{2,}", "-", s).strip("-")

    return s or "template"

def skeleton_template(name: str = "my_tamplate") -> str:
    """Return a ready-to-edit YAML skeleton for a new template."""

    return yaml.safe_dump(
        {
            "version": 1,
            "name": name,
            "output_schema": ["id", "sku", "qty", "price_pennies", "segment"],
            "map": {
                "id": {"from": "ID", "transforms": ["trim"]},
                "sku": {"from": "SKU", "transforms": ["upper"]},
                "qty": {"from": "QTY", "transforms": ["digits_only"]},
                "price_pennies": {"from": "PRICE", "transforms": ["currency_to_minor"]},
                "segment": {"lookup": {"file": "lookups/segments.csv", "key": "CUST_ID", "value": "SEGMENT"}},
            },
            "constants": {},
            "missing": {"policy": "fill", "value": ""},
        },
        sort_keys=False,
        allow_unicode=True,
    )

def load_template_text(path: str | Path) -> str:
    """Read an existing template file into a YAML string."""

    return Path(path).read_text(encoding="utf-8")

def validate_template_yaml(txt: str) -> tuple[bool, str, dict]:
    """
    Check template YAML for required keys and known transform names.

    Returns:
        (ok, message, parsed_dict)
    """

    try:
        data = yaml.safe_load(txt) or {}
    except Exception as e:
        return False, f"YAML error: {e}", {}
    
    problems = []

    for key in ["version", "name", "output_schema", "map"]:
        if key not in data:
            problems.append(f"Missing '{key}'")

    if "output_schema" in data and not isinstance(data["output_schema"], list):
        problems.append("output_schema must be a list")

    if "map" in data and isinstance(data["map"], dict):
        for out_col, spec in data["map"].items():
            if not isinstance(spec, dict):
                problems.append(f"map.{out_col} must be an object")
                continue
            for t in spec.get("transforms", []):
                if t not in BUILTINS:
                    problems.append(f"Unknown transform '{t}' in map.{out_col}")
    ok = len(problems) == 0
    msg = "Valid template" if ok else " • ".join(problems)

    return ok, msg, data

def summarize_template(txt: str) -> pd.DataFrame:
    """Show a simple table of output columns and where they come from."""

    try:
        data = yaml.safe_load(txt) or {}
        schema = data.get("output_schema", [])
        mapping = data.get("map", {})
        rows = []
        for col in schema:
            spec = mapping.get(col, {})
            rows.append(
                {
                    "output": col,
                    "from": spec.get("from", ""),
                    "transforms": ", ".join(spec.get("transforms", [])),
                    "lookup?": "lookup" in spec
                }
            )
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame([])
    
def save_template_text(txt: str) -> tuple[bool, str, str]:
    """
    Persist a validated template to disk.

    Writes to templates/csv/<slug>.yaml when possible; if that directory is
    read-only (e.g., on some Spaces), it falls back to /tmp/<slug>.yaml.

    Returns:
        (ok, message, path_str)
    """

    ok, msg, data = validate_template_yaml(txt)

    if not ok:
        return False, f"Not saved: {msg}", ""
    
    name = slugify(str(data.get("name", "template")))
    dest =TEMPLATE_DIR / f"{name}.yaml"

    # try write to templates/csv; fallback to /tmp if not writable (e.g., on Spaces)
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(txt, encoding="utf-8")
        return True, f"Saved to {dest}", str(dest)
    except Exception as e:
        alt = Path("/tmp") / dest.name
        alt.write_text(txt, encoding="utf-8")
        return True, f"Saved to read-only fallback {alt} (repo dir not writable): {e}", str(alt)
                       