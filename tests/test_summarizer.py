"""Tests for sqlseed.summarizer."""

import pytest

from sqlseed.schema import ColumnDefinition, TableDefinition, SchemaDefinition
from sqlseed.summarizer import (
    summarize_dataset,
    ColumnSummary,
    TableSummary,
    DatasetSummary,
)


def make_col(name: str, col_type: str = "string", nullable: bool = False, unique: bool = False) -> ColumnDefinition:
    return ColumnDefinition(name=name, col_type=col_type, nullable=nullable, unique=unique)


def make_table(name: str, columns: list, row_count: int = 5) -> TableDefinition:
    return TableDefinition(name=name, columns=columns, row_count=row_count)


def make_schema(*tables: TableDefinition) -> SchemaDefinition:
    return SchemaDefinition(tables=list(tables))


class TestSummarizeDataset:
    def test_returns_dataset_summary(self):
        schema = make_schema(make_table("users", [make_col("id", "integer")]))
        dataset = {"users": [{"id": 1}, {"id": 2}]}
        result = summarize_dataset(schema, dataset)
        assert isinstance(result, DatasetSummary)

    def test_table_summary_count(self):
        schema = make_schema(
            make_table("users", [make_col("id", "integer")]),
            make_table("posts", [make_col("title", "string")]),
        )
        dataset = {"users": [{"id": 1}], "posts": [{"title": "hello"}]}
        result = summarize_dataset(schema, dataset)
        assert len(result.table_summaries) == 2

    def test_row_count_in_table_summary(self):
        schema = make_schema(make_table("users", [make_col("id", "integer")]))
        rows = [{"id": i} for i in range(7)]
        result = summarize_dataset(schema, {"users": rows})
        assert result.table_summaries[0].row_count == 7

    def test_column_summaries_populated(self):
        col = make_col("email", "string", nullable=True)
        schema = make_schema(make_table("users", [col]))
        rows = [{"email": "a@b.com"}, {"email": None}]
        result = summarize_dataset(schema, {"users": rows})
        col_summaries = result.table_summaries[0].column_summaries
        assert len(col_summaries) == 1
        assert col_summaries[0].name == "email"
        assert col_summaries[0].nullable is True

    def test_sample_values_limited(self):
        col = make_col("id", "integer")
        schema = make_schema(make_table("items", [col]))
        rows = [{"id": i} for i in range(10)]
        result = summarize_dataset(schema, {"items": rows}, sample_size=3)
        samples = result.table_summaries[0].column_summaries[0].sample_values
        assert len(samples) == 3

    def test_missing_table_in_dataset_gives_zero_rows(self):
        schema = make_schema(make_table("ghosts", [make_col("id", "integer")]))
        result = summarize_dataset(schema, {})
        assert result.table_summaries[0].row_count == 0

    def test_column_summary_str_contains_name(self):
        cs = ColumnSummary(name="age", col_type="integer", nullable=False, unique=False, sample_values=[25, 30])
        assert "age" in str(cs)
        assert "integer" in str(cs)

    def test_column_summary_str_shows_flags(self):
        cs = ColumnSummary(name="email", col_type="string", nullable=True, unique=True, sample_values=[])
        text = str(cs)
        assert "nullable" in text
        assert "unique" in text

    def test_table_summary_str_contains_table_name(self):
        ts = TableSummary(name="orders", row_count=4, column_summaries=[])
        assert "orders" in str(ts)
        assert "4" in str(ts)

    def test_dataset_summary_str_joins_tables(self):
        schema = make_schema(
            make_table("users", [make_col("id", "integer")]),
            make_table("posts", [make_col("title", "string")]),
        )
        dataset = {"users": [{"id": 1}], "posts": [{"title": "hi"}]}
        result = summarize_dataset(schema, dataset)
        text = str(result)
        assert "users" in text
        assert "posts" in text
