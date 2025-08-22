"""
src/csvbot/templates.py
"""


from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
import yaml


@dataclass
class Template:

    name: str
    version: int
    output_schema: List[str]
    mapping: Dict[str, Any]
    constants: Dict[str, Any]
    missing: Dict[str, Any]

    @staticmethod
    def from_yaml(path: str | Path) -> "Template":

        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return Template(
            name=data.get("name", "template"),
            version=int(data.get("version", 1)),
            output_schema=list(data["output_schema"]),
            mapping=dict(data["map"]),
            constants=dict(data.get("constants", {})),
            missing=dict(data.get("missing", {"policy": "fill", "value": ""} ))
        )
    

class TemplateRegistry:

    def __init__(self):
        """Simple on-disk template loader with memoization."""
        self._cache: Dict[str, Template] = {}

    def get(self, path: str | Path) -> Template:

        key = str(Path(path).resolve())

        if key not in self._cache:
            self._cache[key] = Template.from_yaml(key)
        return self._cache[key]