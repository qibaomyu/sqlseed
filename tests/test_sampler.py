"""Tests for sqlseed.sampler."""

from __future__ import annotations

import pytest

from sqlseed.sampler import SampleOptions, sample_dataset, sample_table
from sqlseed.schema import ColumnDefinition, TableDefinition


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_col(name: str = "id", col_type: str = "integer") -> ColumnDefinition:
    return ColumnDefinition(name=name, col_type=col_type)


def make_table(name: str = "users", row_count: int = 10) -> TableDefinition:
    return TableDefinition(
        name=name,
        row_count=row_count,
        columns=[make_col("id", "integer"), make_col("name", "string")],
    )


def make_rows(n: int = 10) -> list:
    return [{"id": i, "name": f"user_{i}"} for i in range(n)]


# ---------------------------------------------------------------------------
# SampleOptions validation
# ---------------------------------------------------------------------------

class TestSampleOptions:
    def test_valid_fraction(self):
        opt = SampleOptions(fraction=0.5)
        assert opt.fraction == 0.5

    def test_fraction_out_of_range_raises(self):
        with pytest.raises(ValueError, match="fraction"):
            SampleOptions(fraction=1.5)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            SampleOptions(n=-1)

    def test_both_fraction_and_n_raises(self):
        with pytest.raises(ValueError, match="not both"):
            SampleOptions(fraction=0.5, n=3)


# ---------------------------------------------------------------------------
# sample_table
# ---------------------------------------------------------------------------

class TestSampleTable:
    def test_fraction_returns_correct_count(self):
        rows = make_rows(20)
        result = sample_table(rows, make_table(row_count=20), SampleOptions(fraction=0.5, seed=0))
        assert len(result) == 10

    def test_n_returns_exact_count(self):
        rows = make_rows(20)
        result = sample_table(rows, make_table(row_count=20), SampleOptions(n=7, seed=0))
        assert len(result) == 7

    def test_n_larger_than_rows_capped(self):
        rows = make_rows(5)
        result = sample_table(rows, make_table(row_count=5), SampleOptions(n=100, seed=0))
        assert len(result) == 5

    def test_no_options_returns_all(self):
        rows = make_rows(10)
        result = sample_table(rows, make_table(), SampleOptions())
        assert len(result) == 10

    def test_seed_is_reproducible(self):
        rows = make_rows(20)
        t = make_table(row_count=20)
        r1 = sample_table(rows, t, SampleOptions(n=5, seed=42))
        r2 = sample_table(rows, t, SampleOptions(n=5, seed=42))
        assert r1 == r2

    def test_different_seeds_differ(self):
        rows = make_rows(20)
        t = make_table(row_count=20)
        r1 = sample_table(rows, t, SampleOptions(n=5, seed=1))
        r2 = sample_table(rows, t, SampleOptions(n=5, seed=2))
        assert r1 != r2

    def test_shuffle_false_preserves_order(self):
        rows = make_rows(10)
        result = sample_table(rows, make_table(), SampleOptions(n=5, shuffle=False))
        assert result == rows[:5]


# ---------------------------------------------------------------------------
# sample_dataset
# ---------------------------------------------------------------------------

class TestSampleDataset:
    def test_all_tables_sampled(self):
        tables = [make_table("users", 10), make_table("orders", 10)]
        dataset = {"users": make_rows(10), "orders": make_rows(10)}
        result = sample_dataset(dataset, tables, SampleOptions(n=4, seed=0))
        assert len(result["users"]) == 4
        assert len(result["orders"]) == 4

    def test_unknown_table_excluded(self):
        tables = [make_table("users", 10)]
        dataset = {"users": make_rows(10), "orphan": make_rows(5)}
        result = sample_dataset(dataset, tables, SampleOptions(n=3, seed=0))
        assert "orphan" not in result
