"""Tests for sqlseed.exporter — SQL and CSV export functionality."""

import pytest

from sqlseed.schema import ColumnDefinition, TableDefinition
from sqlseed.exporter import (
    _escape_sql_value,
    export_table_to_sql,
    export_table_to_csv,
    export_dataset,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_col(name: str, col_type: str = "string", primary_key: bool = False) -> ColumnDefinition:
    return ColumnDefinition(name=name, col_type=col_type, primary_key=primary_key)


def make_table(name: str, cols=None) -> TableDefinition:
    if cols is None:
        cols = [make_col("id", "integer", primary_key=True), make_col("name", "string")]
    return TableDefinition(name=name, columns=cols, row_count=2)


SAMPLE_ROWS = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]


# ---------------------------------------------------------------------------
# _escape_sql_value
# ---------------------------------------------------------------------------

class TestEscapeSqlValue:
    def test_none_becomes_null(self):
        assert _escape_sql_value(None) == "NULL"

    def test_integer(self):
        assert _escape_sql_value(42) == "42"

    def test_float(self):
        assert _escape_sql_value(3.14) == "3.14"

    def test_string_quoted(self):
        assert _escape_sql_value("hello") == "'hello'"

    def test_string_with_single_quote_escaped(self):
        assert _escape_sql_value("it's") == "'it''s'"

    def test_bool_true(self):
        assert _escape_sql_value(True) == "1"

    def test_bool_false(self):
        assert _escape_sql_value(False) == "0"


# ---------------------------------------------------------------------------
# export_table_to_sql
# ---------------------------------------------------------------------------

class TestExportTableToSql:
    def test_empty_rows_returns_empty_string(self):
        table = make_table("users")
        assert export_table_to_sql(table, []) == ""

    def test_insert_statements_generated(self):
        table = make_table("users")
        sql = export_table_to_sql(table, SAMPLE_ROWS)
        assert "INSERT INTO users" in sql
        assert "'Alice'" in sql
        assert "'Bob'" in sql

    def test_row_count_matches(self):
        table = make_table("users")
        sql = export_table_to_sql(table, SAMPLE_ROWS)
        assert sql.count("INSERT INTO") == 2

    def test_include_transaction_wraps_statements(self):
        table = make_table("users")
        sql = export_table_to_sql(table, SAMPLE_ROWS, include_transaction=True)
        assert sql.startswith("BEGIN;")
        assert "COMMIT;" in sql

    def test_no_transaction_by_default(self):
        table = make_table("users")
        sql = export_table_to_sql(table, SAMPLE_ROWS)
        assert "BEGIN;" not in sql


# ---------------------------------------------------------------------------
# export_table_to_csv
# ---------------------------------------------------------------------------

class TestExportTableToCsv:
    def test_header_row_present(self):
        table = make_table("users")
        csv_out = export_table_to_csv(table, SAMPLE_ROWS)
        first_line = csv_out.splitlines()[0]
        assert first_line == "id,name"

    def test_data_rows_present(self):
        table = make_table("users")
        csv_out = export_table_to_csv(table, SAMPLE_ROWS)
        assert "Alice" in csv_out
        assert "Bob" in csv_out

    def test_empty_rows_only_header(self):
        table = make_table("users")
        csv_out = export_table_to_csv(table, [])
        lines = [l for l in csv_out.splitlines() if l]
        assert lines == ["id,name"]


# ---------------------------------------------------------------------------
# export_dataset
# ---------------------------------------------------------------------------

class TestExportDataset:
    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported export format"):
            export_dataset({}, {}, fmt="json")

    def test_sql_dataset_combines_tables(self):
        t1 = make_table("users")
        t2 = make_table("orders", cols=[make_col("id", "integer", True), make_col("total", "float")])
        dataset = {
            "users": SAMPLE_ROWS,
            "orders": [{"id": 1, "total": 9.99}],
        }
        out = export_dataset({"users": t1, "orders": t2}, dataset, fmt="sql")
        assert "INSERT INTO users" in out
        assert "INSERT INTO orders" in out

    def test_csv_dataset_combines_tables(self):
        t1 = make_table("users")
        dataset = {"users": SAMPLE_ROWS}
        out = export_dataset({"users": t1}, dataset, fmt="csv")
        assert "id,name" in out
        assert "Alice" in out
