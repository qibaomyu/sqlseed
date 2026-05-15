"""Tests for sqlseed.renderer."""

from __future__ import annotations

import pytest

from sqlseed.renderer import RenderOptions, RenderResult, render
from sqlseed.schema import ColumnDefinition, SchemaDefinition, TableDefinition


def make_col(name: str, col_type: str = "string", nullable: bool = False) -> ColumnDefinition:
    return ColumnDefinition(name=name, col_type=col_type, nullable=nullable)


def make_schema(*table_specs: tuple[str, int]) -> SchemaDefinition:
    tables = []
    for tname, row_count in table_specs:
        cols = [
            make_col("id", "integer"),
            make_col("label", "string"),
        ]
        tables.append(TableDefinition(name=tname, columns=cols, row_count=row_count))
    return SchemaDefinition(tables=tables)


class TestRenderResult:
    def test_ok_when_no_errors(self):
        r = RenderResult()
        assert r.ok is True

    def test_not_ok_when_errors_present(self):
        r = RenderResult(errors=["something went wrong"])
        assert r.ok is False


class TestRender:
    def test_basic_render_returns_dataset(self):
        schema = make_schema(("products", 5))
        result = render(schema, RenderOptions(fmt="json"))
        assert result.ok
        assert "products" in result.dataset
        assert len(result.dataset["products"]) == 5

    def test_json_format_populates_outputs(self):
        schema = make_schema(("items", 3))
        result = render(schema, RenderOptions(fmt="json"))
        assert "items" in result.outputs
        assert result.outputs["items"].startswith("{")

    def test_jsonl_format_populates_outputs(self):
        schema = make_schema(("items", 4))
        result = render(schema, RenderOptions(fmt="jsonl"))
        lines = result.outputs["items"].strip().split("\n")
        assert len(lines) == 4

    def test_csv_format_populates_outputs(self):
        schema = make_schema(("things", 2))
        result = render(schema, RenderOptions(fmt="csv"))
        lines = result.outputs["things"].split("\n")
        # header + 2 data rows
        assert len(lines) == 3

    def test_sql_format_outputs_empty(self):
        schema = make_schema(("orders", 3))
        result = render(schema, RenderOptions(fmt="sql"))
        assert result.ok
        # sql is handled by exporter; outputs dict is empty
        assert result.outputs == {}

    def test_table_filter_limits_output(self):
        schema = make_schema(("users", 3), ("posts", 5))
        result = render(schema, RenderOptions(fmt="json", tables=["users"]))
        assert "users" in result.dataset
        assert "posts" not in result.dataset

    def test_invalid_schema_returns_errors(self):
        # A schema with no columns should fail validation
        bad_table = TableDefinition(name="empty", columns=[], row_count=1)
        schema = SchemaDefinition(tables=[bad_table])
        result = render(schema, RenderOptions(validate=True))
        assert not result.ok
        assert len(result.errors) > 0

    def test_skip_validation_bypasses_errors(self):
        bad_table = TableDefinition(name="empty", columns=[], row_count=1)
        schema = SchemaDefinition(tables=[bad_table])
        result = render(schema, RenderOptions(validate=False, fmt="json"))
        # No validation errors; dataset generated (empty rows expected)
        assert result.ok

    def test_default_options_used_when_none_provided(self):
        schema = make_schema(("nodes", 2))
        result = render(schema)
        assert result.ok
