"""Tests for sqlseed.sorter."""

import pytest
from sqlseed.sorter import SortKey, SortOptions, sort_table, sort_dataset


def make_rows():
    return [
        {"id": 3, "name": "Charlie", "score": 80},
        {"id": 1, "name": "Alice", "score": 95},
        {"id": 2, "name": "Bob", "score": None},
    ]


class TestSortKey:
    def test_extract_plain_value(self):
        sk = SortKey(column="id")
        row = {"id": 42}
        assert sk.extract(row) == 42

    def test_extract_missing_column_returns_none(self):
        sk = SortKey(column="missing")
        assert sk.extract({"id": 1}) is None

    def test_extract_applies_key_fn(self):
        sk = SortKey(column="name", key_fn=str.lower)
        assert sk.extract({"name": "ALICE"}) == "alice"

    def test_key_fn_skipped_for_none(self):
        sk = SortKey(column="name", key_fn=str.lower)
        assert sk.extract({"name": None}) is None


class TestSortOptions:
    def test_defaults(self):
        opts = SortOptions()
        assert opts.keys == []
        assert opts.nulls_last is True

    def test_invalid_keys_type_raises(self):
        with pytest.raises(TypeError):
            SortOptions(keys="id")


class TestSortTable:
    def test_empty_keys_returns_copy(self):
        rows = make_rows()
        result = sort_table(rows, SortOptions())
        assert result == rows
        assert result is not rows

    def test_sort_ascending_by_id(self):
        rows = make_rows()
        opts = SortOptions(keys=[SortKey(column="id", ascending=True)])
        result = sort_table(rows, opts)
        ids = [r["id"] for r in result]
        assert ids == [1, 2, 3]

    def test_sort_descending_by_id(self):
        rows = make_rows()
        opts = SortOptions(keys=[SortKey(column="id", ascending=False)])
        result = sort_table(rows, opts)
        ids = [r["id"] for r in result]
        assert ids == [3, 2, 1]

    def test_nulls_sorted_last_by_default(self):
        rows = make_rows()
        opts = SortOptions(keys=[SortKey(column="score", ascending=True)])
        result = sort_table(rows, opts)
        assert result[-1]["score"] is None

    def test_original_list_not_mutated(self):
        rows = make_rows()
        original_first = rows[0]["id"]
        opts = SortOptions(keys=[SortKey(column="id")])
        sort_table(rows, opts)
        assert rows[0]["id"] == original_first

    def test_sort_by_name_ascending(self):
        rows = make_rows()
        opts = SortOptions(keys=[SortKey(column="name", ascending=True)])
        result = sort_table(rows, opts)
        names = [r["name"] for r in result]
        assert names == sorted(names)


class TestSortDataset:
    def test_sorts_specified_table(self):
        dataset = {"users": make_rows()}
        opts = {"users": SortOptions(keys=[SortKey(column="id")])}
        result = sort_dataset(dataset, opts)
        ids = [r["id"] for r in result["users"]]
        assert ids == [1, 2, 3]

    def test_unspecified_table_unchanged(self):
        rows = make_rows()
        dataset = {"users": rows, "orders": [{"id": 2}, {"id": 1}]}
        opts = {"users": SortOptions(keys=[SortKey(column="id")])}
        result = sort_dataset(dataset, opts)
        assert result["orders"] == [{"id": 2}, {"id": 1}]

    def test_returns_new_dict(self):
        dataset = {"users": make_rows()}
        result = sort_dataset(dataset, {})
        assert result is not dataset
