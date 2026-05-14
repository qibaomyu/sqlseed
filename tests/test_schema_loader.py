"""Unit tests for sqlseed.schema_loader module."""
import textwrap
from pathlib import Path

import pytest
import yaml

from sqlseed.schema_loader import load_schema_from_dict, load_schema_from_yaml


SAMPLE_DICT = {
    "tables": [
        {
            "name": "users",
            "row_count": 20,
            "columns": [
                {"name": "id", "type": "integer", "primary_key": True},
                {"name": "email", "type": "email", "unique": True},
                {"name": "name", "type": "name", "nullable": True},
            ],
        }
    ]
}


class TestLoadSchemaFromDict:
    def test_basic_load(self):
        schema = load_schema_from_dict(SAMPLE_DICT)
        assert len(schema.tables) == 1
        assert schema.tables[0].name == "users"

    def test_row_count_propagated(self):
        schema = load_schema_from_dict(SAMPLE_DICT)
        assert schema.tables[0].row_count == 20

    def test_columns_parsed(self):
        schema = load_schema_from_dict(SAMPLE_DICT)
        cols = schema.tables[0].columns
        assert len(cols) == 3
        assert cols[1].unique is True
        assert cols[2].nullable is True

    def test_empty_tables(self):
        schema = load_schema_from_dict({"tables": []})
        assert schema.tables == []

    def test_invalid_column_type_raises(self):
        bad = {"tables": [{"name": "t", "columns": [{"name": "x", "type": "blob"}]}]}
        with pytest.raises(ValueError, match="Invalid column type"):
            load_schema_from_dict(bad)


class TestLoadSchemaFromYaml:
    def test_load_from_file(self, tmp_path):
        schema_file = tmp_path / "schema.yaml"
        schema_file.write_text(yaml.dump(SAMPLE_DICT), encoding="utf-8")
        schema = load_schema_from_yaml(schema_file)
        assert schema.get_table("users") is not None

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_schema_from_yaml(tmp_path / "missing.yaml")

    def test_non_mapping_yaml_raises(self, tmp_path):
        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("- item1\n- item2\n", encoding="utf-8")
        with pytest.raises(ValueError, match="Expected a YAML mapping"):
            load_schema_from_yaml(bad_file)
