"""Unit tests for sqlseed.schema module."""
import pytest

from sqlseed.schema import ColumnDefinition, SchemaDefinition, TableDefinition


def make_column(**kwargs):
    defaults = {"name": "id", "type": "integer", "primary_key": True}
    defaults.update(kwargs)
    return ColumnDefinition(**defaults)


class TestColumnDefinition:
    def test_valid_type_accepted(self):
        col = make_column(type="string")
        assert col.type == "string"

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Invalid column type"):
            make_column(type="blob")

    def test_defaults(self):
        col = make_column()
        assert col.nullable is False
        assert col.unique is False
        assert col.foreign_key is None
        assert col.constraints == {}


class TestTableDefinition:
    def test_valid_table(self):
        cols = [make_column(name="id"), make_column(name="email", type="email")]
        table = TableDefinition(name="users", columns=cols, row_count=5)
        assert table.name == "users"
        assert table.row_count == 5

    def test_row_count_zero_raises(self):
        with pytest.raises(ValueError, match="row_count must be"):
            TableDefinition(name="t", columns=[make_column()], row_count=0)

    def test_duplicate_columns_raises(self):
        cols = [make_column(name="id"), make_column(name="id")]
        with pytest.raises(ValueError, match="Duplicate column"):
            TableDefinition(name="t", columns=cols)

    def test_get_column_found(self):
        cols = [make_column(name="id"), make_column(name="age", type="integer")]
        table = TableDefinition(name="t", columns=cols)
        assert table.get_column("age").name == "age"

    def test_get_column_missing(self):
        table = TableDefinition(name="t", columns=[make_column()])
        assert table.get_column("nonexistent") is None


class TestSchemaDefinition:
    def _schema(self):
        cols = [make_column()]
        return SchemaDefinition(tables=[
            TableDefinition(name="users", columns=cols),
            TableDefinition(name="orders", columns=cols),
        ])

    def test_table_names(self):
        assert self._schema().table_names() == ["users", "orders"]

    def test_get_table_found(self):
        assert self._schema().get_table("orders").name == "orders"

    def test_get_table_missing(self):
        assert self._schema().get_table("missing") is None
