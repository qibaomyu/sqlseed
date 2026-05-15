"""Tests for sqlseed.merger."""

import pytest

from sqlseed.merger import MergeOptions, merge_datasets


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_rows(*dicts):
    return list(dicts)


# ---------------------------------------------------------------------------
# MergeOptions
# ---------------------------------------------------------------------------

class TestMergeOptions:
    def test_defaults(self):
        opts = MergeOptions()
        assert opts.deduplicate is False
        assert opts.dedup_key is None
        assert opts.fill_missing is True
        assert opts.fill_value is None

    def test_deduplicate_requires_key(self):
        with pytest.raises(ValueError, match="dedup_key"):
            MergeOptions(deduplicate=True)

    def test_deduplicate_with_key_ok(self):
        opts = MergeOptions(deduplicate=True, dedup_key="id")
        assert opts.dedup_key == "id"


# ---------------------------------------------------------------------------
# merge_datasets
# ---------------------------------------------------------------------------

class TestMergeDatasets:
    def test_single_dataset_passthrough(self):
        ds = {"users": make_rows({"id": 1}, {"id": 2})}
        result = merge_datasets([ds])
        assert len(result["users"]) == 2

    def test_rows_concatenated_across_datasets(self):
        ds1 = {"users": make_rows({"id": 1})}
        ds2 = {"users": make_rows({"id": 2})}
        result = merge_datasets([ds1, ds2])
        assert len(result["users"]) == 2

    def test_disjoint_tables_both_present(self):
        ds1 = {"users": make_rows({"id": 1})}
        ds2 = {"orders": make_rows({"id": 10})}
        result = merge_datasets([ds1, ds2])
        assert "users" in result
        assert "orders" in result

    def test_fill_missing_keys_with_none(self):
        ds1 = {"users": make_rows({"id": 1, "name": "Alice"})}
        ds2 = {"users": make_rows({"id": 2})}
        result = merge_datasets([ds1, ds2], MergeOptions(fill_missing=True))
        for row in result["users"]:
            assert "name" in row

    def test_fill_missing_uses_custom_fill_value(self):
        ds1 = {"t": make_rows({"a": 1, "b": 2})}
        ds2 = {"t": make_rows({"a": 3})}
        result = merge_datasets([ds1, ds2], MergeOptions(fill_missing=True, fill_value="N/A"))
        missing_row = next(r for r in result["t"] if r["a"] == 3)
        assert missing_row["b"] == "N/A"

    def test_no_fill_missing_leaves_keys_uneven(self):
        ds1 = {"t": make_rows({"a": 1, "b": 2})}
        ds2 = {"t": make_rows({"a": 3})}
        result = merge_datasets([ds1, ds2], MergeOptions(fill_missing=False))
        keys = [set(r.keys()) for r in result["t"]]
        assert keys[0] != keys[1]

    def test_deduplication_removes_duplicate_keys(self):
        rows = make_rows({"id": 1, "v": "a"}, {"id": 1, "v": "b"}, {"id": 2, "v": "c"})
        ds = {"t": rows}
        opts = MergeOptions(deduplicate=True, dedup_key="id")
        result = merge_datasets([ds], opts)
        assert len(result["t"]) == 2

    def test_deduplication_keeps_first_occurrence(self):
        rows = make_rows({"id": 1, "v": "first"}, {"id": 1, "v": "second"})
        ds = {"t": rows}
        opts = MergeOptions(deduplicate=True, dedup_key="id")
        result = merge_datasets([ds], opts)
        assert result["t"][0]["v"] == "first"

    def test_empty_datasets_list_returns_empty(self):
        result = merge_datasets([])
        assert result == {}

    def test_empty_table_in_dataset(self):
        ds = {"users": []}
        result = merge_datasets([ds])
        assert result["users"] == []
