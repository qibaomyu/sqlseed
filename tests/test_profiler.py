"""Tests for sqlseed.profiler."""

from __future__ import annotations

import pytest

from sqlseed.schema import ColumnDefinition, SchemaDefinition, TableDefinition
from sqlseed.profiler import (
    ColumnProfile,
    TableProfile,
    SchemaProfile,
    profile_schema,
    _profile_table,
)


def make_col(
    name="id",
    data_type="integer",
    nullable=False,
    primary_key=False,
    unique=False,
    foreign_key=None,
):
    return ColumnDefinition(
        name=name,
        data_type=data_type,
        nullable=nullable,
        primary_key=primary_key,
        unique=unique,
        foreign_key=foreign_key,
    )


def make_table(name="users", row_count=10, columns=None):
    if columns is None:
        columns = [make_col()]
    return TableDefinition(name=name, row_count=row_count, columns=columns)


def make_schema(tables=None):
    if tables is None:
        tables = [make_table()]
    return SchemaDefinition(tables=tables)


class TestColumnProfile:
    def test_str_no_flags(self):
        cp = ColumnProfile("email", "varchar", False, False, False, False)
        assert "email" in str(cp)
        assert "varchar" in str(cp)
        assert "[" not in str(cp)

    def test_str_with_flags(self):
        cp = ColumnProfile("id", "integer", False, True, True, False)
        result = str(cp)
        assert "PK" in result
        assert "UNIQUE" in result

    def test_str_nullable_and_fk(self):
        cp = ColumnProfile("user_id", "integer", True, False, False, True)
        result = str(cp)
        assert "NULLABLE" in result
        assert "FK" in result


class TestTableProfile:
    def test_column_count(self):
        tp = _profile_table(make_table(columns=[make_col("a"), make_col("b")]))
        assert tp.column_count == 2

    def test_nullable_count(self):
        cols = [make_col("a", nullable=True), make_col("b", nullable=False)]
        tp = _profile_table(make_table(columns=cols))
        assert tp.nullable_count == 1

    def test_pk_columns(self):
        cols = [make_col("id", primary_key=True), make_col("name")]
        tp = _profile_table(make_table(columns=cols))
        assert tp.pk_columns == ["id"]

    def test_str_contains_table_name(self):
        tp = _profile_table(make_table(name="orders"))
        assert "orders" in str(tp)


class TestSchemaProfile:
    def test_table_count(self):
        schema = make_schema([make_table("a"), make_table("b")])
        sp = profile_schema(schema)
        assert sp.table_count == 2

    def test_total_rows(self):
        schema = make_schema([make_table(row_count=5), make_table(row_count=15)])
        sp = profile_schema(schema)
        assert sp.total_rows == 20

    def test_summary_contains_table_names(self):
        schema = make_schema([make_table("customers"), make_table("orders")])
        sp = profile_schema(schema)
        summary = sp.summary()
        assert "customers" in summary
        assert "orders" in summary

    def test_summary_header(self):
        schema = make_schema([make_table()])
        sp = profile_schema(schema)
        assert "Schema Profile" in sp.summary()

    def test_empty_schema(self):
        schema = SchemaDefinition(tables=[])
        sp = profile_schema(schema)
        assert sp.table_count == 0
        assert sp.total_rows == 0
