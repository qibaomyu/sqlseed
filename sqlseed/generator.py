"""Data generator module for sqlseed.

Generates realistic fake data based on column definitions.
"""

import random
import string
from datetime import date, datetime, timedelta
from typing import Any

from sqlseed.schema import ColumnDefinition, TableDefinition

_FIRST_NAMES = ["Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Hank"]
_LAST_NAMES = ["Smith", "Jones", "Williams", "Brown", "Davis", "Miller", "Wilson"]
_WORDS = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing"]


def _random_string(max_length: int = 32) -> str:
    length = min(max_length, random.randint(4, 16))
    return "".join(random.choices(string.ascii_lowercase, k=length))


def _generate_value(col: ColumnDefinition, row_index: int) -> Any:
    """Generate a single value for the given column definition."""
    if col.primary_key:
        return row_index + 1

    name_lower = col.name.lower()

    if col.col_type == "integer":
        return random.randint(0, 10_000)

    if col.col_type == "float":
        return round(random.uniform(0.0, 1_000.0), 4)

    if col.col_type == "boolean":
        return random.choice([True, False])

    if col.col_type == "date":
        base = date(2020, 1, 1)
        return (base + timedelta(days=random.randint(0, 1460))).isoformat()

    if col.col_type == "datetime":
        base = datetime(2020, 1, 1)
        return (base + timedelta(seconds=random.randint(0, 126_144_000))).isoformat()

    # col_type == "string" — apply heuristics based on column name
    if "email" in name_lower:
        user = random.choice(_FIRST_NAMES).lower()
        domain = _random_string(6)
        return f"{user}{row_index}@{domain}.com"

    if "name" in name_lower:
        return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"

    if "phone" in name_lower:
        digits = "".join(random.choices(string.digits, k=10))
        return f"+1{digits}"

    if "url" in name_lower or "website" in name_lower:
        slug = _random_string(8)
        return f"https://www.{slug}.example.com"

    max_len = col.max_length or 64
    return _random_string(max_len)


def generate_rows(table: TableDefinition) -> list[dict[str, Any]]:
    """Generate all rows for a table according to its definition."""
    rows = []
    for i in range(table.row_count):
        row = {col.name: _generate_value(col, i) for col in table.columns}
        rows.append(row)
    return rows


def generate_dataset(tables: list[TableDefinition]) -> dict[str, list[dict[str, Any]]]:
    """Generate data for every table and return a mapping of table name -> rows."""
    return {table.name: generate_rows(table) for table in tables}
