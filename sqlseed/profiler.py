"""Schema profiling: summarize tables, column types, and nullability stats."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from sqlseed.schema import SchemaDefinition, TableDefinition


@dataclass
class ColumnProfile:
    name: str
    data_type: str
    nullable: bool
    primary_key: bool
    unique: bool
    has_foreign_key: bool

    def __str__(self) -> str:
        flags = []
        if self.primary_key:
            flags.append("PK")
        if self.unique:
            flags.append("UNIQUE")
        if self.nullable:
            flags.append("NULLABLE")
        if self.has_foreign_key:
            flags.append("FK")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        return f"  {self.name}: {self.data_type}{flag_str}"


@dataclass
class TableProfile:
    name: str
    row_count: int
    columns: List[ColumnProfile] = field(default_factory=list)

    @property
    def column_count(self) -> int:
        return len(self.columns)

    @property
    def nullable_count(self) -> int:
        return sum(1 for c in self.columns if c.nullable)

    @property
    def pk_columns(self) -> List[str]:
        return [c.name for c in self.columns if c.primary_key]

    def __str__(self) -> str:
        lines = [
            f"Table: {self.name}",
            f"  rows: {self.row_count}, columns: {self.column_count}, nullable: {self.nullable_count}",
        ]
        lines.extend(str(col) for col in self.columns)
        return "\n".join(lines)


@dataclass
class SchemaProfile:
    table_profiles: List[TableProfile] = field(default_factory=list)

    @property
    def table_count(self) -> int:
        return len(self.table_profiles)

    @property
    def total_rows(self) -> int:
        return sum(t.row_count for t in self.table_profiles)

    def summary(self) -> str:
        lines = [
            f"Schema Profile: {self.table_count} table(s), {self.total_rows} total row(s)",
            "-" * 40,
        ]
        for tp in self.table_profiles:
            lines.append(str(tp))
            lines.append("")
        return "\n".join(lines).rstrip()


def _profile_table(table: TableDefinition) -> TableProfile:
    col_profiles = [
        ColumnProfile(
            name=col.name,
            data_type=col.data_type,
            nullable=col.nullable,
            primary_key=col.primary_key,
            unique=col.unique,
            has_foreign_key=col.foreign_key is not None,
        )
        for col in table.columns
    ]
    return TableProfile(name=table.name, row_count=table.row_count, columns=col_profiles)


def profile_schema(schema: SchemaDefinition) -> SchemaProfile:
    """Build a SchemaProfile from a SchemaDefinition."""
    return SchemaProfile(table_profiles=[_profile_table(t) for t in schema.tables])
