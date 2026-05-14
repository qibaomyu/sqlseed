"""Schema validation utilities for sqlseed."""

from dataclasses import dataclass
from typing import List
from sqlseed.schema import SchemaDefinition, TableDefinition, ColumnDefinition


@dataclass
class ValidationError:
    table: str
    column: str | None
    message: str

    def __str__(self) -> str:
        if self.column:
            return f"[{self.table}.{self.column}] {self.message}"
        return f"[{self.table}] {self.message}"


@dataclass
class ValidationResult:
    errors: List[ValidationError]

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def __str__(self) -> str:
        if self.valid:
            return "Schema is valid."
        lines = ["Schema validation failed:"]
        for err in self.errors:
            lines.append(f"  - {err}")
        return "\n".join(lines)


def _validate_column(table_name: str, col: ColumnDefinition) -> List[ValidationError]:
    errors: List[ValidationError] = []

    if not col.name or not col.name.strip():
        errors.append(ValidationError(table_name, col.name, "Column name must not be empty."))

    if col.nullable and col.primary_key:
        errors.append(ValidationError(table_name, col.name, "Primary key column cannot be nullable."))

    if col.col_type == "enum" and not col.values:
        errors.append(ValidationError(table_name, col.name, "Enum column must define at least one value."))

    if col.col_type != "enum" and col.values:
        errors.append(ValidationError(table_name, col.name, "'values' is only valid for enum columns."))

    return errors


def _validate_table(table: TableDefinition) -> List[ValidationError]:
    errors: List[ValidationError] = []

    if not table.name or not table.name.strip():
        errors.append(ValidationError(table.name or "<unknown>", None, "Table name must not be empty."))

    if table.row_count < 1:
        errors.append(ValidationError(table.name, None, f"row_count must be >= 1, got {table.row_count}."))

    if not table.columns:
        errors.append(ValidationError(table.name, None, "Table must define at least one column."))

    pk_columns = [c for c in table.columns if c.primary_key]
    if len(pk_columns) > 1:
        errors.append(ValidationError(table.name, None, "Table must not have more than one primary key column."))

    for col in table.columns:
        errors.extend(_validate_column(table.name, col))

    return errors


def validate_schema(schema: SchemaDefinition) -> ValidationResult:
    """Validate a SchemaDefinition and return a ValidationResult."""
    errors: List[ValidationError] = []

    if not schema.tables:
        errors.append(ValidationError("<schema>", None, "Schema must define at least one table."))

    for table in schema.tables:
        errors.extend(_validate_table(table))

    return ValidationResult(errors=errors)
