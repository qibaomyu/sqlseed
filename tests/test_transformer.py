"""Tests for sqlseed.transformer module."""

import pytest
from sqlseed.transformer import (
    ColumnTransform,
    TableTransformer,
    TransformOptions,
    transform_dataset,
)


def make_rows(n: int = 3) -> list:
    return [{"id": i, "name": f"user_{i}", "score": i * 10} for i in range(1, n + 1)]


class TestColumnTransform:
    def test_transforms_existing_column(self):
        ct = ColumnTransform(column="score", fn=lambda x: x * 2)
        row = {"id": 1, "score": 5}
        result = ct.apply(row)
        assert result["score"] == 10

    def test_skips_missing_column(self):
        ct = ColumnTransform(column="missing", fn=lambda x: x * 2)
        row = {"id": 1, "score": 5}
        result = ct.apply(row)
        assert result == {"id": 1, "score": 5}

    def test_does_not_mutate_original(self):
        ct = ColumnTransform(column="name", fn=str.upper)
        original = {"id": 1, "name": "alice"}
        ct.apply(original)
        assert original["name"] == "alice"


class TestTableTransformer:
    def test_add_returns_self(self):
        tt = TableTransformer(table_name="users")
        result = tt.add(lambda row: row)
        assert result is tt

    def test_applies_transforms_in_order(self):
        tt = TableTransformer(table_name="users")
        tt.add(lambda row: {**row, "val": row["val"] + 1})
        tt.add(lambda row: {**row, "val": row["val"] * 2})
        rows = [{"val": 3}]
        result = tt.apply(rows)
        assert result[0]["val"] == 8  # (3+1)*2

    def test_empty_transforms_returns_rows_unchanged(self):
        tt = TableTransformer(table_name="orders")
        rows = make_rows(2)
        assert tt.apply(rows) == rows

    def test_applies_to_all_rows(self):
        tt = TableTransformer(table_name="users")
        tt.add(lambda row: {**row, "score": 0})
        rows = make_rows(4)
        result = tt.apply(rows)
        assert all(r["score"] == 0 for r in result)


class TestTransformDataset:
    def test_no_options_returns_dataset_unchanged(self):
        dataset = {"users": make_rows(2)}
        result = transform_dataset(dataset)
        assert result == dataset

    def test_empty_transformers_returns_dataset_unchanged(self):
        dataset = {"users": make_rows(2)}
        result = transform_dataset(dataset, TransformOptions())
        assert result == dataset

    def test_transforms_matching_table(self):
        tt = TableTransformer("users")
        tt.add(lambda row: {**row, "name": "anon"})
        opts = TransformOptions()
        opts.add_transformer(tt)
        dataset = {"users": make_rows(3)}
        result = transform_dataset(dataset, opts)
        assert all(r["name"] == "anon" for r in result["users"])

    def test_unmatched_tables_pass_through(self):
        tt = TableTransformer("users")
        tt.add(lambda row: {**row, "name": "anon"})
        opts = TransformOptions()
        opts.add_transformer(tt)
        orders = [{"id": 1, "total": 99}]
        dataset = {"users": make_rows(1), "orders": orders}
        result = transform_dataset(dataset, opts)
        assert result["orders"] == orders

    def test_column_transform_integration(self):
        ct = ColumnTransform(column="score", fn=lambda x: -1)
        tt = TableTransformer("users")
        tt.add(ct.apply)
        opts = TransformOptions()
        opts.add_transformer(tt)
        dataset = {"users": make_rows(2)}
        result = transform_dataset(dataset, opts)
        assert all(r["score"] == -1 for r in result["users"])
