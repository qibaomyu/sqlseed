"""Tests for sqlseed.filter module."""

import pytest
from sqlseed.filter import FilterCondition, TableFilter, filter_table, filter_dataset


def make_rows():
    return [
        {"id": 1, "age": 25, "active": True, "name": "Alice"},
        {"id": 2, "age": 17, "active": False, "name": "Bob"},
        {"id": 3, "age": 30, "active": True, "name": "Carol"},
        {"id": 4, "age": 15, "active": True, "name": "Dave"},
    ]


class TestFilterCondition:
    def test_matches_true(self):
        cond = FilterCondition("age", lambda v: v >= 18, "adult")
        assert cond.matches({"age": 25}) is True

    def test_matches_false(self):
        cond = FilterCondition("age", lambda v: v >= 18, "adult")
        assert cond.matches({"age": 15}) is False

    def test_missing_column_passes_none_to_predicate(self):
        cond = FilterCondition("missing", lambda v: v is None)
        assert cond.matches({"age": 5}) is True

    def test_description_stored(self):
        cond = FilterCondition("age", lambda v: True, "always true")
        assert cond.description == "always true"


class TestTableFilter:
    def test_apply_single_condition(self):
        tf = TableFilter("users")
        tf.add("age", lambda v: v >= 18)
        result = tf.apply(make_rows())
        assert len(result) == 2
        assert all(r["age"] >= 18 for r in result)

    def test_apply_multiple_conditions(self):
        tf = TableFilter("users")
        tf.add("age", lambda v: v >= 18)
        tf.add("active", lambda v: v is True)
        result = tf.apply(make_rows())
        assert len(result) == 2
        assert all(r["age"] >= 18 and r["active"] for r in result)

    def test_apply_no_conditions_returns_all(self):
        tf = TableFilter("users")
        result = tf.apply(make_rows())
        assert len(result) == 4

    def test_apply_no_matches_returns_empty(self):
        tf = TableFilter("users")
        tf.add("age", lambda v: v > 100)
        result = tf.apply(make_rows())
        assert result == []

    def test_chained_add_returns_self(self):
        tf = TableFilter("users")
        result = tf.add("age", lambda v: True)
        assert result is tf


class TestFilterTable:
    def test_none_filter_returns_all(self):
        rows = make_rows()
        assert filter_table(rows, None) == rows

    def test_filter_applied(self):
        tf = TableFilter("users")
        tf.add("active", lambda v: v is True)
        result = filter_table(make_rows(), tf)
        assert len(result) == 3


class TestFilterDataset:
    def test_no_filters_returns_original(self):
        dataset = {"users": make_rows()}
        result = filter_dataset(dataset)
        assert result == dataset

    def test_filter_applied_to_matching_table(self):
        tf = TableFilter("users")
        tf.add("age", lambda v: v >= 18)
        dataset = {"users": make_rows(), "orders": [{"id": 1}]}
        result = filter_dataset(dataset, {"users": tf})
        assert len(result["users"]) == 2
        assert result["orders"] == [{"id": 1}]

    def test_unknown_table_filter_ignored(self):
        tf = TableFilter("nonexistent")
        tf.add("id", lambda v: False)
        dataset = {"users": make_rows()}
        result = filter_dataset(dataset, {"nonexistent": tf})
        assert len(result["users"]) == 4
