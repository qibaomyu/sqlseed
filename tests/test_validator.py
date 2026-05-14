"""Tests for sqlseed.validator."""

import pytest
from sqlseed.schema import ColumnDefinition, TableDefinition, SchemaDefinition
from sqlseed.validator import validate_schema, ValidationError, ValidationResult


def make_col(name="id", col_type="integer", primary_key=False, nullable=False, values=None):
    return ColumnDefinition(
        name=name,
        col_type=col_type,
        primary_key=primary_key,
        nullable=nullable,
        values=values or [],
    )


def make_table(name="users", row_count=10, columns=None):
    if columns is None:
        columns = [make_col("id", primary_key=True), make_col("name", col_type="string")]
    return TableDefinition(name=name, row_count=row_count, columns=columns)


def make_schema(tables=None):
    if tables is None:
        tables = [make_table()]
    return SchemaDefinition(tables=tables)


class TestValidateSchema:
    def test_valid_schema_returns_no_errors(self):
        result = validate_schema(make_schema())
        assert result.valid
        assert result.errors == []

    def test_empty_tables_list_is_invalid(self):
        schema = SchemaDefinition(tables=[])
        result = validate_schema(schema)
        assert not result.valid
        assert any("at least one table" in str(e) for e in result.errors)

    def test_row_count_zero_is_invalid(self):
        schema = make_schema(tables=[make_table(row_count=0)])
        result = validate_schema(schema)
        assert not result.valid
        assert any("row_count" in str(e) for e in result.errors)

    def test_negative_row_count_is_invalid(self):
        schema = make_schema(tables=[make_table(row_count=-5)])
        result = validate_schema(schema)
        assert not result.valid

    def test_table_with_no_columns_is_invalid(self):
        schema = make_schema(tables=[make_table(columns=[])])
        result = validate_schema(schema)
        assert not result.valid
        assert any("at least one column" in str(e) for e in result.errors)

    def test_multiple_primary_keys_is_invalid(self):
        cols = [make_col("id", primary_key=True), make_col("uid", primary_key=True)]
        schema = make_schema(tables=[make_table(columns=cols)])
        result = validate_schema(schema)
        assert not result.valid
        assert any("primary key" in str(e) for e in result.errors)

    def test_nullable_primary_key_is_invalid(self):
        cols = [make_col("id", primary_key=True, nullable=True)]
        schema = make_schema(tables=[make_table(columns=cols)])
        result = validate_schema(schema)
        assert not result.valid
        assert any("nullable" in str(e) for e in result.errors)

    def test_enum_without_values_is_invalid(self):
        cols = [make_col("status", col_type="enum", values=[])]
        schema = make_schema(tables=[make_table(columns=cols)])
        result = validate_schema(schema)
        assert not result.valid
        assert any("value" in str(e) for e in result.errors)

    def test_non_enum_with_values_is_invalid(self):
        cols = [make_col("name", col_type="string", values=["a", "b"])]
        schema = make_schema(tables=[make_table(columns=cols)])
        result = validate_schema(schema)
        assert not result.valid
        assert any("enum" in str(e) for e in result.errors)

    def test_validation_result_str_valid(self):
        result = validate_schema(make_schema())
        assert "valid" in str(result).lower()

    def test_validation_result_str_invalid(self):
        schema = SchemaDefinition(tables=[])
        result = validate_schema(schema)
        assert "failed" in str(result).lower()
