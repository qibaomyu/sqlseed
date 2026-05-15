"""Filter generated dataset rows based on column conditions."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from sqlseed.schema import TableDefinition


@dataclass
class FilterCondition:
    """A single filter condition for a column."""

    column: str
    predicate: Callable[[Any], bool]
    description: str = ""

    def matches(self, row: Dict[str, Any]) -> bool:
        value = row.get(self.column)
        return self.predicate(value)


@dataclass
class TableFilter:
    """A collection of conditions applied to a table's rows."""

    table_name: str
    conditions: List[FilterCondition] = field(default_factory=list)

    def add(self, column: str, predicate: Callable[[Any], bool], description: str = "") -> "TableFilter":
        self.conditions.append(FilterCondition(column, predicate, description))
        return self

    def apply(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return only rows matching all conditions."""
        result = []
        for row in rows:
            if all(c.matches(row) for c in self.conditions):
                result.append(row)
        return result


def filter_table(
    rows: List[Dict[str, Any]],
    table_filter: Optional[TableFilter],
) -> List[Dict[str, Any]]:
    """Apply a TableFilter to rows, returning filtered list."""
    if table_filter is None:
        return rows
    return table_filter.apply(rows)


def filter_dataset(
    dataset: Dict[str, List[Dict[str, Any]]],
    filters: Optional[Dict[str, TableFilter]] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """Apply per-table filters to an entire dataset."""
    if not filters:
        return dataset
    return {
        table_name: filter_table(rows, filters.get(table_name))
        for table_name, rows in dataset.items()
    }
