"""Summarizer: produces a human-readable text summary of a generated dataset."""

from dataclasses import dataclass
from typing import Any

from sqlseed.schema import SchemaDefinition


@dataclass
class ColumnSummary:
    name: str
    col_type: str
    nullable: bool
    unique: bool
    sample_values: list[Any]

    def __str__(self) -> str:
        flags = []
        if self.nullable:
            flags.append("nullable")
        if self.unique:
            flags.append("unique")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        samples = ", ".join(repr(v) for v in self.sample_values[:3])
        return f"    {self.name} ({self.col_type}){flag_str}: {samples}"


@dataclass
class TableSummary:
    name: str
    row_count: int
    column_summaries: list[ColumnSummary]

    def __str__(self) -> str:
        lines = [f"Table: {self.name} ({self.row_count} rows)"]
        for cs in self.column_summaries:
            lines.append(str(cs))
        return "\n".join(lines)


@dataclass
class DatasetSummary:
    table_summaries: list[TableSummary]

    def __str__(self) -> str:
        return "\n\n".join(str(ts) for ts in self.table_summaries)


def summarize_dataset(
    schema: SchemaDefinition,
    dataset: dict[str, list[dict[str, Any]]],
    sample_size: int = 3,
) -> DatasetSummary:
    """Build a DatasetSummary from a schema and generated dataset rows."""
    table_summaries: list[TableSummary] = []

    for table_def in schema.tables:
        rows = dataset.get(table_def.name, [])
        col_summaries: list[ColumnSummary] = []

        for col in table_def.columns:
            samples = [
                row[col.name]
                for row in rows[:sample_size]
                if col.name in row
            ]
            col_summaries.append(
                ColumnSummary(
                    name=col.name,
                    col_type=col.col_type,
                    nullable=col.nullable,
                    unique=col.unique,
                    sample_values=samples,
                )
            )

        table_summaries.append(
            TableSummary(
                name=table_def.name,
                row_count=len(rows),
                column_summaries=col_summaries,
            )
        )

    return DatasetSummary(table_summaries=table_summaries)
