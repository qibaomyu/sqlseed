"""Output formatters for generated dataset rows."""

from __future__ import annotations

import json
from typing import Any

from sqlseed.schema import TableDefinition


SUPPORTED_FORMATS = ("json", "jsonl", "csv", "sql")


def format_as_json(table: TableDefinition, rows: list[dict[str, Any]]) -> str:
    """Return rows as a pretty-printed JSON array."""
    payload = {"table": table.name, "rows": rows}
    return json.dumps(payload, indent=2, default=str)


def format_as_jsonl(rows: list[dict[str, Any]]) -> str:
    """Return rows as newline-delimited JSON (one object per line)."""
    lines = [json.dumps(row, default=str) for row in rows]
    return "\n".join(lines)


def format_as_csv(table: TableDefinition, rows: list[dict[str, Any]]) -> str:
    """Return rows as CSV text with a header line."""
    if not rows:
        return ""
    headers = [col.name for col in table.columns]
    lines = [",".join(headers)]
    for row in rows:
        values = []
        for h in headers:
            v = row.get(h)
            if v is None:
                values.append("")
            else:
                cell = str(v).replace('"', '""')
                if "," in cell or '"' in cell or "\n" in cell:
                    cell = f'"{cell}"'
                values.append(cell)
        lines.append(",".join(values))
    return "\n".join(lines)


def format_dataset(
    tables: dict[str, TableDefinition],
    dataset: dict[str, list[dict[str, Any]]],
    fmt: str,
) -> dict[str, str]:
    """Apply *fmt* formatter to every table in *dataset*.

    Returns a mapping of table name -> formatted string.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from {SUPPORTED_FORMATS}.")

    result: dict[str, str] = {}
    for table_name, rows in dataset.items():
        table = tables[table_name]
        if fmt == "json":
            result[table_name] = format_as_json(table, rows)
        elif fmt == "jsonl":
            result[table_name] = format_as_jsonl(rows)
        elif fmt == "csv":
            result[table_name] = format_as_csv(table, rows)
        # sql is handled by exporter; return empty placeholder
        elif fmt == "sql":
            result[table_name] = ""
    return result
