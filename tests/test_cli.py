"""Tests for the sqlseed CLI, including the --profile flag."""

from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from sqlseed.cli import build_parser, run


@pytest.fixture()
def schema_file(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        tables:
          - name: users
            row_count: 5
            columns:
              - name: id
                type: integer
                primary_key: true
              - name: username
                type: varchar
                unique: true
    """)
    p = tmp_path / "schema.yaml"
    p.write_text(content)
    return p


def test_validate_only_valid_schema(schema_file, capsys):
    parser = build_parser()
    args = parser.parse_args([str(schema_file), "--validate"])
    code = run(args)
    assert code == 0
    assert "valid" in capsys.readouterr().out.lower()


def test_missing_schema_file(tmp_path, capsys):
    parser = build_parser()
    args = parser.parse_args([str(tmp_path / "missing.yaml")])
    code = run(args)
    assert code == 1
    assert "not found" in capsys.readouterr().err.lower()


def test_profile_flag_prints_summary(schema_file, capsys):
    parser = build_parser()
    args = parser.parse_args([str(schema_file), "--profile"])
    code = run(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "Schema Profile" in out
    assert "users" in out


def test_sql_output_creates_files(schema_file, tmp_path, capsys):
    parser = build_parser()
    args = parser.parse_args([
        str(schema_file), "--format", "sql", "--output-dir", str(tmp_path / "out")
    ])
    code = run(args)
    assert code == 0
    files = list((tmp_path / "out").glob("*.sql"))
    assert len(files) >= 1


def test_csv_output_creates_files(schema_file, tmp_path, capsys):
    parser = build_parser()
    args = parser.parse_args([
        str(schema_file), "--format", "csv", "--output-dir", str(tmp_path / "out")
    ])
    code = run(args)
    assert code == 0
    files = list((tmp_path / "out").glob("*.csv"))
    assert len(files) >= 1


def test_invalid_yaml_returns_error(tmp_path, capsys):
    bad = tmp_path / "bad.yaml"
    bad.write_text(": : : not valid yaml :::")
    parser = build_parser()
    args = parser.parse_args([str(bad)])
    code = run(args)
    assert code == 1
