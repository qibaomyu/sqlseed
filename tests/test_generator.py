"""Tests for sqlseed.generator module."""

import pytest

from sqlseed.schema import ColumnDefinition, TableDefinition
from sqlseed.generator import generate_rows, generate_dataset


def make_table(columns, row_count=5, name="users"):
    return TableDefinition(name=name, columns=columns, row_count=row_count)


def make_col(name, col_type, primary_key=False, max_length=None):
    return ColumnDefinition(
        name=name, col_type=col_type, primary_key=primary_key, max_length=max_length
    )


class TestGenerateRows:
    def test_row_count_matches(self):
        table = make_table([make_col("id", "integer", primary_key=True)], row_count=10)
        rows = generate_rows(table)
        assert len(rows) == 10

    def test_primary_key_sequential(self):
        table = make_table([make_col("id", "integer", primary_key=True)], row_count=5)
        rows = generate_rows(table)
        assert [r["id"] for r in rows] == [1, 2, 3, 4, 5]

    def test_integer_column_type(self):
        table = make_table([make_col("age", "integer")], row_count=20)
        rows = generate_rows(table)
        assert all(isinstance(r["age"], int) for r in rows)

    def test_float_column_type(self):
        table = make_table([make_col("score", "float")], row_count=10)
        rows = generate_rows(table)
        assert all(isinstance(r["score"], float) for r in rows)

    def test_boolean_column_type(self):
        table = make_table([make_col("active", "boolean")], row_count=20)
        rows = generate_rows(table)
        assert all(isinstance(r["active"], bool) for r in rows)

    def test_date_column_is_string(self):
        table = make_table([make_col("created_at", "date")], row_count=5)
        rows = generate_rows(table)
        assert all(isinstance(r["created_at"], str) for r in rows)

    def test_datetime_column_is_string(self):
        table = make_table([make_col("updated_at", "datetime")], row_count=5)
        rows = generate_rows(table)
        assert all(isinstance(r["updated_at"], str) for r in rows)

    def test_email_heuristic(self):
        table = make_table([make_col("email", "string")], row_count=10)
        rows = generate_rows(table)
        assert all("@" in r["email"] for r in rows)

    def test_name_heuristic_returns_string(self):
        table = make_table([make_col("full_name", "string")], row_count=5)
        rows = generate_rows(table)
        assert all(isinstance(r["full_name"], str) for r in rows)

    def test_row_has_all_columns(self):
        cols = [
            make_col("id", "integer", primary_key=True),
            make_col("email", "string"),
            make_col("score", "float"),
        ]
        table = make_table(cols, row_count=3)
        rows = generate_rows(table)
        for row in rows:
            assert set(row.keys()) == {"id", "email", "score"}

    def test_zero_rows(self):
        table = make_table([make_col("id", "integer", primary_key=True)], row_count=0)
        assert generate_rows(table) == []


class TestGenerateDataset:
    def test_returns_all_tables(self):
        tables = [
            make_table([make_col("id", "integer", primary_key=True)], name="users"),
            make_table([make_col("id", "integer", primary_key=True)], name="posts"),
        ]
        dataset = generate_dataset(tables)
        assert set(dataset.keys()) == {"users", "posts"}

    def test_row_counts_per_table(self):
        tables = [
            make_table([make_col("id", "integer", primary_key=True)], row_count=3, name="a"),
            make_table([make_col("id", "integer", primary_key=True)], row_count=7, name="b"),
        ]
        dataset = generate_dataset(tables)
        assert len(dataset["a"]) == 3
        assert len(dataset["b"]) == 7
