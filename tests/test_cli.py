"""Tests for the sqlseed CLI."""

import textwrap
from pathlib import Path

import pytest

from sqlseed.cli import run


SAMPLE_SCHEMA = textwrap.dedent("""\
    tables:
      users:
        row_count: 5
        columns:
          id:
            type: integer
            primary_key: true
          name:
            type: string
            nullable: false
          email:
            type: string
            nullable: true
""")


@pytest.fixture()
def schema_file(tmp_path: Path) -> Path:
    path = tmp_path / "schema.yaml"
    path.write_text(SAMPLE_SCHEMA)
    return path


def test_validate_only_valid_schema(schema_file, capsys):
    code = run([str(schema_file), "--validate-only"])
    assert code == 0
    captured = capsys.readouterr()
    assert "valid" in captured.out


def test_missing_schema_file(tmp_path):
    code = run([str(tmp_path / "nonexistent.yaml")])
    assert code == 1


def test_sql_output_creates_files(schema_file, tmp_path):
    output_dir = tmp_path / "out"
    code = run([str(schema_file), "--format", "sql", "--output", str(output_dir)])
    assert code == 0
    assert (output_dir / "users.sql").exists()


def test_csv_output_creates_files(schema_file, tmp_path):
    output_dir = tmp_path / "out_csv"
    code = run([str(schema_file), "--format", "csv", "--output", str(output_dir)])
    assert code == 0
    assert (output_dir / "users.csv").exists()


def test_invalid_schema_reports_errors(tmp_path, capsys):
    bad_schema = tmp_path / "bad.yaml"
    bad_schema.write_text(
        textwrap.dedent("""\
            tables:
              broken:
                row_count: -1
                columns:
                  id:
                    type: integer
                    primary_key: true
        """)
    )
    code = run([str(bad_schema)])
    assert code == 1
    captured = capsys.readouterr()
    assert "validation failed" in captured.err.lower()


def test_output_message_lists_tables(schema_file, tmp_path, capsys):
    output_dir = tmp_path / "out"
    run([str(schema_file), "--output", str(output_dir)])
    captured = capsys.readouterr()
    assert "users" in captured.out
