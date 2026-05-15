"""Tests for sqlseed.formatter."""

from __future__ import annotations

import json

import pytest

from sqlseed.formatter import (
    format_as_csv,
    format_as_json,
    format_as_jsonl,
    format_dataset,
    SUPPORTED_FORMATS,
)
from sqlseed.schema import ColumnDefinition, TableDefinition


def make_col(name: str, col_type: str = "string", nullable: bool = False) -> ColumnDefinition:
    return ColumnDefinition(name=name, col_type=col_type, nullable=nullable)


def make_table(name: str, cols: list[ColumnDefinition], row_count: int = 2) -> TableDefinition:
    return TableDefinition(name=name, columns=cols, row_count=row_count)


SAMPLE_ROWS = [
    {"id": 1, "username": "alice", "score": 42},
    {"id": 2, "username": "bob", "score": None},
]

SAMPLE_TABLE = make_table(
    "users",
    [
        make_col("id", "integer"),
        make_col("username", "string"),
        make_col("score", "integer", nullable=True),
    ],
)


class TestFormatAsJson:
    def test_returns_valid_json(self):
        result = format_as_json(SAMPLE_TABLE, SAMPLE_ROWS)
        parsed = json.loads(result)
        assert parsed["table"] == "users"
        assert len(parsed["rows"]) == 2

    def test_row_values_preserved(self):
        result = json.loads(format_as_json(SAMPLE_TABLE, SAMPLE_ROWS))
        assert result["rows"][0]["username"] == "alice"

    def test_empty_rows(self):
        result = json.loads(format_as_json(SAMPLE_TABLE, []))
        assert result["rows"] == []


class TestFormatAsJsonl:
    def test_line_count_matches_rows(self):
        result = format_as_jsonl(SAMPLE_ROWS)
        lines = result.strip().split("\n")
        assert len(lines) == 2

    def test_each_line_is_valid_json(self):
        result = format_as_jsonl(SAMPLE_ROWS)
        for line in result.split("\n"):
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_empty_rows_returns_empty_string(self):
        assert format_as_jsonl([]) == ""


class TestFormatAsCsv:
    def test_header_row_present(self):
        result = format_as_csv(SAMPLE_TABLE, SAMPLE_ROWS)
        first_line = result.split("\n")[0]
        assert first_line == "id,username,score"

    def test_none_becomes_empty(self):
        result = format_as_csv(SAMPLE_TABLE, SAMPLE_ROWS)
        lines = result.split("\n")
        assert lines[2].endswith(",")

    def test_empty_rows_returns_empty_string(self):
        assert format_as_csv(SAMPLE_TABLE, []) == ""

    def test_comma_in_value_is_quoted(self):
        rows = [{"id": 1, "username": "last, first", "score": 0}]
        result = format_as_csv(SAMPLE_TABLE, rows)
        assert '"last, first"' in result


class TestFormatDataset:
    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported format"):
            format_dataset({}, {}, "xml")

    def test_json_format(self):
        tables = {"users": SAMPLE_TABLE}
        dataset = {"users": SAMPLE_ROWS}
        result = format_dataset(tables, dataset, "json")
        assert "users" in result
        parsed = json.loads(result["users"])
        assert parsed["table"] == "users"

    def test_jsonl_format(self):
        tables = {"users": SAMPLE_TABLE}
        dataset = {"users": SAMPLE_ROWS}
        result = format_dataset(tables, dataset, "jsonl")
        assert len(result["users"].split("\n")) == 2

    def test_supported_formats_constant(self):
        assert "json" in SUPPORTED_FORMATS
        assert "csv" in SUPPORTED_FORMATS
