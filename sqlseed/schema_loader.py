"""Load and parse schema definitions from YAML files."""
from pathlib import Path
from typing import Any, Dict

import yaml

from sqlseed.schema import ColumnDefinition, SchemaDefinition, TableDefinition


def _parse_column(data: Dict[str, Any]) -> ColumnDefinition:
    """Parse a single column dict into a ColumnDefinition."""
    return ColumnDefinition(
        name=data["name"],
        type=data["type"],
        nullable=data.get("nullable", False),
        unique=data.get("unique", False),
        primary_key=data.get("primary_key", False),
        foreign_key=data.get("foreign_key"),
        default=data.get("default"),
        constraints=data.get("constraints", {}),
    )


def _parse_table(data: Dict[str, Any]) -> TableDefinition:
    """Parse a single table dict into a TableDefinition."""
    columns = [_parse_column(col) for col in data.get("columns", [])]
    return TableDefinition(
        name=data["name"],
        columns=columns,
        row_count=data.get("row_count", 10),
    )


def load_schema_from_dict(data: Dict[str, Any]) -> SchemaDefinition:
    """Load a SchemaDefinition from a plain Python dict."""
    tables = [_parse_table(t) for t in data.get("tables", [])]
    return SchemaDefinition(tables=tables)


def load_schema_from_yaml(path: str | Path) -> SchemaDefinition:
    """Load a SchemaDefinition from a YAML file path."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    if not isinstance(raw, dict):
        raise ValueError(f"Expected a YAML mapping at top level, got {type(raw).__name__}")
    return load_schema_from_dict(raw)
