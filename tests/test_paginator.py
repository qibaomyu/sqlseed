"""Tests for sqlseed.paginator."""

import pytest
from sqlseed.paginator import (
    PaginationOptions,
    Page,
    PaginatedTable,
    paginate_table,
    paginate_dataset,
)


def make_rows(n: int):
    return [{"id": i, "val": f"v{i}"} for i in range(n)]


class TestPaginationOptions:
    def test_defaults(self):
        opts = PaginationOptions()
        assert opts.page_size == 100
        assert opts.start_page == 1

    def test_invalid_page_size_raises(self):
        with pytest.raises(ValueError, match="page_size"):
            PaginationOptions(page_size=0)

    def test_invalid_start_page_raises(self):
        with pytest.raises(ValueError, match="start_page"):
            PaginationOptions(start_page=0)


class TestPage:
    def test_size_property(self):
        page = Page(table="users", page_number=1, rows=make_rows(5))
        assert page.size == 5

    def test_str_contains_table_and_number(self):
        page = Page(table="orders", page_number=3, rows=make_rows(2))
        s = str(page)
        assert "orders" in s
        assert "3" in s


class TestPaginateTable:
    def test_empty_rows_produces_one_empty_page(self):
        result = paginate_table("users", [], PaginationOptions(page_size=10))
        assert result.page_count == 1
        assert result.pages[0].size == 0

    def test_exact_multiple_produces_correct_page_count(self):
        rows = make_rows(20)
        result = paginate_table("users", rows, PaginationOptions(page_size=5))
        assert result.page_count == 4

    def test_non_multiple_adds_partial_last_page(self):
        rows = make_rows(11)
        result = paginate_table("users", rows, PaginationOptions(page_size=5))
        assert result.page_count == 3
        assert result.pages[-1].size == 1

    def test_total_rows_preserved(self):
        rows = make_rows(37)
        result = paginate_table("items", rows, PaginationOptions(page_size=10))
        assert result.total_rows == 37

    def test_start_page_offset_applied(self):
        rows = make_rows(5)
        result = paginate_table("t", rows, PaginationOptions(page_size=5, start_page=3))
        assert result.pages[0].page_number == 3

    def test_page_numbers_are_sequential(self):
        rows = make_rows(15)
        result = paginate_table("t", rows, PaginationOptions(page_size=5, start_page=2))
        numbers = [p.page_number for p in result]
        assert numbers == [2, 3, 4]

    def test_table_name_set_on_pages(self):
        rows = make_rows(3)
        result = paginate_table("products", rows, PaginationOptions(page_size=10))
        assert all(p.table == "products" for p in result)


class TestPaginateDataset:
    def test_all_tables_present(self):
        dataset = {"users": make_rows(5), "orders": make_rows(8)}
        result = paginate_dataset(dataset, PaginationOptions(page_size=3))
        assert set(result.keys()) == {"users", "orders"}

    def test_each_table_paginated_independently(self):
        dataset = {"a": make_rows(10), "b": make_rows(4)}
        result = paginate_dataset(dataset, PaginationOptions(page_size=5))
        assert result["a"].page_count == 2
        assert result["b"].page_count == 1
