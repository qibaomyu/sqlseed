"""Tests for sqlseed.pipeline module."""

import pytest
from sqlseed.schema import SchemaDefinition, TableDefinition, ColumnDefinition
from sqlseed.pipeline import PipelineOptions, run_pipeline
from sqlseed.transformer import ColumnTransform, TableTransformer, TransformOptions
from sqlseed.sampler import SampleOptions
from sqlseed.renderer import RenderOptions


def make_col(name: str, col_type: str = "string", primary_key: bool = False) -> ColumnDefinition:
    return ColumnDefinition(name=name, col_type=col_type, primary_key=primary_key)


def make_schema(row_count: int = 5) -> SchemaDefinition:
    table = TableDefinition(
        name="users",
        row_count=row_count,
        columns=[make_col("id", "integer", primary_key=True), make_col("email", "email")],
    )
    return SchemaDefinition(tables=[table])


class TestRunPipeline:
    def test_returns_render_result(self):
        result = run_pipeline(make_schema())
        assert hasattr(result, "ok")
        assert hasattr(result, "dataset")

    def test_ok_for_valid_schema(self):
        result = run_pipeline(make_schema())
        assert result.ok

    def test_dataset_contains_table(self):
        result = run_pipeline(make_schema(row_count=3))
        assert "users" in result.dataset
        assert len(result.dataset["users"]) == 3

    def test_invalid_schema_returns_errors(self):
        table = TableDefinition(
            name="bad",
            row_count=-1,
            columns=[make_col("id", "integer", primary_key=True)],
        )
        schema = SchemaDefinition(tables=[table])
        result = run_pipeline(schema)
        assert not result.ok
        assert len(result.errors) > 0

    def test_transform_applied(self):
        ct = ColumnTransform(column="email", fn=lambda _: "masked@example.com")
        tt = TableTransformer("users")
        tt.add(ct.apply)
        opts = PipelineOptions(transform_options=TransformOptions())
        opts.transform_options.add_transformer(tt)
        result = run_pipeline(make_schema(row_count=4), opts)
        assert all(r["email"] == "masked@example.com" for r in result.dataset["users"])

    def test_sample_applied(self):
        sample_opts = SampleOptions(fraction=0.5, seed=42)
        opts = PipelineOptions(sample_options=sample_opts)
        result = run_pipeline(make_schema(row_count=10), opts)
        assert len(result.dataset["users"]) <= 10

    def test_none_options_uses_defaults(self):
        result = run_pipeline(make_schema(), None)
        assert result.ok
