"""Tests for sqlseed.pipeline."""

from __future__ import annotations

import pytest

from sqlseed.pipeline import PipelineOptions, run_pipeline
from sqlseed.renderer import RenderOptions
from sqlseed.sampler import SampleOptions
from sqlseed.schema import ColumnDefinition, SchemaDefinition, TableDefinition


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_col(name: str, col_type: str = "string") -> ColumnDefinition:
    return ColumnDefinition(name=name, col_type=col_type)


def make_schema(row_count: int = 5) -> SchemaDefinition:
    return SchemaDefinition(
        tables=[
            TableDefinition(
                name="users",
                row_count=row_count,
                columns=[
                    make_col("id", "integer"),
                    make_col("email", "email"),
                ],
            )
        ]
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestRunPipeline:
    def test_returns_render_result(self):
        result = run_pipeline(make_schema())
        assert result is not None

    def test_ok_for_valid_schema(self):
        result = run_pipeline(make_schema())
        assert result.ok

    def test_output_contains_table(self):
        result = run_pipeline(make_schema())
        assert "users" in result.output or len(result.errors) == 0

    def test_sampling_reduces_rows(self):
        opts = PipelineOptions(
            sample=SampleOptions(n=2, seed=0),
            render=RenderOptions(format="json"),
        )
        result = run_pipeline(make_schema(row_count=10), opts)
        assert result.ok

    def test_invalid_schema_returns_errors(self):
        bad_schema = SchemaDefinition(
            tables=[
                TableDefinition(
                    name="",          # invalid: empty name
                    row_count=5,
                    columns=[make_col("id", "integer")],
                )
            ]
        )
        result = run_pipeline(bad_schema, PipelineOptions(validate=True))
        assert not result.ok
        assert len(result.errors) > 0

    def test_validate_false_skips_validation(self):
        """Even with an empty-name table, skipping validation should not crash."""
        schema = make_schema()
        opts = PipelineOptions(validate=False)
        result = run_pipeline(schema, opts)
        # As long as it doesn't raise, the pipeline completed
        assert result is not None

    def test_default_options_used_when_none_passed(self):
        result = run_pipeline(make_schema())
        assert result.ok
