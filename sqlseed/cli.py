"""Command-line interface for sqlseed."""

import argparse
import sys
from pathlib import Path

from sqlseed.schema_loader import load_schema_from_yaml
from sqlseed.validator import validate_schema
from sqlseed.generator import generate_dataset
from sqlseed.exporter import export_dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sqlseed",
        description="Generate realistic test data from a YAML schema definition.",
    )
    parser.add_argument("schema", help="Path to the YAML schema file.")
    parser.add_argument(
        "--format",
        choices=["sql", "csv"],
        default="sql",
        help="Output format (default: sql).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output directory. Defaults to current directory.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the schema without generating data.",
    )
    return parser


def run(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Error: schema file '{schema_path}' not found.", file=sys.stderr)
        return 1

    try:
        schema = load_schema_from_yaml(str(schema_path))
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading schema: {exc}", file=sys.stderr)
        return 1

    result = validate_schema(schema)
    if not result.valid:
        print("Schema validation failed:", file=sys.stderr)
        for error in result.errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    if args.validate_only:
        print("Schema is valid.")
        return 0

    output_dir = Path(args.output) if args.output else Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = generate_dataset(schema)
    export_dataset(dataset, schema, output_dir=str(output_dir), fmt=args.format)

    table_names = [t.name for t in schema.tables]
    print(
        f"Generated data for {len(table_names)} table(s): {', '.join(table_names)}"
    )
    print(f"Output written to: {output_dir}")
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
