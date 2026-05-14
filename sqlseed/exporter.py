"""Export generated dataset to various output formats (SQL INSERT, CSV)."""

import csv
import io
from typing import Dict, List, Any

from sqlseed.schema import TableDefinition


def _escape_sql_value(value: Any) -> str:
    """Escape a Python value for use in a SQL INSERT statement."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    # Escape single quotes in strings
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def export_table_to_sql(
    table: TableDefinition,
    rows: List[Dict[str, Any]],
    include_transaction: bool = False,
) -> str:
    """Generate SQL INSERT statements for a table's rows.

    Args:
        table: The table definition.
        rows: List of row dicts produced by generate_rows.
        include_transaction: Wrap statements in BEGIN/COMMIT.

    Returns:
        A string of SQL INSERT statements.
    """
    if not rows:
        return ""

    column_names = [col.name for col in table.columns]
    col_list = ", ".join(column_names)
    lines: List[str] = []

    if include_transaction:
        lines.append("BEGIN;")

    for row in rows:
        values = ", ".join(_escape_sql_value(row.get(col)) for col in column_names)
        lines.append(f"INSERT INTO {table.name} ({col_list}) VALUES ({values});")

    if include_transaction:
        lines.append("COMMIT;")

    return "\n".join(lines) + "\n"


def export_table_to_csv(
    table: TableDefinition,
    rows: List[Dict[str, Any]],
) -> str:
    """Export table rows as a CSV string.

    Args:
        table: The table definition.
        rows: List of row dicts produced by generate_rows.

    Returns:
        A CSV-formatted string with a header row.
    """
    column_names = [col.name for col in table.columns]
    output = io.StringIO()
    writer = csv.DictWriter(
        output, fieldnames=column_names, extrasaction="ignore", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def export_dataset(
    tables: Dict[str, TableDefinition],
    dataset: Dict[str, List[Dict[str, Any]]],
    fmt: str = "sql",
    include_transaction: bool = False,
) -> str:
    """Export an entire dataset (all tables) to a single string.

    Args:
        tables: Mapping of table name to TableDefinition.
        dataset: Mapping of table name to list of rows.
        fmt: Output format — 'sql' or 'csv'.
        include_transaction: (SQL only) wrap all inserts in a transaction.

    Returns:
        Combined output string for all tables.
    """
    if fmt not in ("sql", "csv"):
        raise ValueError(f"Unsupported export format: '{fmt}'. Use 'sql' or 'csv'.")

    parts: List[str] = []
    for table_name, table_def in tables.items():
        rows = dataset.get(table_name, [])
        if fmt == "sql":
            parts.append(
                export_table_to_sql(table_def, rows, include_transaction=include_transaction)
            )
        else:
            parts.append(export_table_to_csv(table_def, rows))

    separator = "\n" if fmt == "sql" else "\n"
    return separator.join(parts)
