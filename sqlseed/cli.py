"""CLI entry point for sqlseed."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlseed.schema_loader import load_schema_from_yaml
from sqlseed.validator import validate_schema
from sqlseed.generator import generate_dataset
from sqlseed.exporter import export_dataset
from sqlseed.profiler import profile_schema


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sqlseed",
        description="Generate realistic test data from a YAML schema definition.",
    )
    parser.add_argument("schema", help="Path to the YAML schema file")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the schema and exit without generating data",
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Print a profile summary of the schema and exit",
    )
    parser.add_argument(
        "--format",
        choices=["sql", "csv"],
        default="sql",
        help="Output format (default: sql)",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write output files (default: current directory)",
    )
    return parser


def _load_and_validate_schema(schema_path: Path):
    """Load a schema from *schema_path* and validate it.

    Returns the validated schema on success.  Prints an error message to
    stderr and returns ``None`` on failure so the caller can propagate the
    appropriate exit code.
    """
    try:
        schema = load_schema_from_yaml(str(schema_path))
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading schema: {exc}", file=sys.stderr)
        return None

    result = validate_schema(schema)
    if not result.is_valid:
        print("Schema validation failed:", file=sys.stderr)
        for err in result.errors:
            print(f"  {err}", file=sys.stderr)
        return None

    return schema


def run(args: argparse.Namespace) -> int:
    """Execute the command described by *args* and return an exit code."""
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Error: schema file not found: {schema_path}", file=sys.stderr)
        return 1

    schema = _load_and_validate_schema(schema_path)
    if schema is None:
        return 1

    if args.validate:
        print("Schema is valid.")
        return 0

    if args.profile:
        sp = profile_schema(schema)
        print(sp.summary())
        return 0

    dataset = generate_dataset(schema)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    export_dataset(dataset, fmt=args.format, output_dir=str(output_dir))
    print(f"Data written to {output_dir} ({args.format} format).")
    return 0


def main() -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":  # pragma: no cover
    main()
