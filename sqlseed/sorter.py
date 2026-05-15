"""Dataset row sorting utilities for sqlseed."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class SortKey:
    """Defines a single sort key for a column."""

    column: str
    ascending: bool = True
    key_fn: Optional[Callable[[Any], Any]] = None

    def extract(self, row: Dict[str, Any]) -> Any:
        """Extract and optionally transform the sort value from a row."""
        value = row.get(self.column)
        if self.key_fn is not None and value is not None:
            return self.key_fn(value)
        return value


@dataclass
class SortOptions:
    """Options controlling how rows are sorted."""

    keys: List[SortKey] = field(default_factory=list)
    nulls_last: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.keys, list):
            raise TypeError("keys must be a list of SortKey instances")


def _sort_key_fn(
    keys: List[SortKey], nulls_last: bool
) -> Callable[[Dict[str, Any]], tuple]:
    """Build a comparison key function from a list of SortKeys."""

    def _key(row: Dict[str, Any]) -> tuple:
        parts = []
        for sk in keys:
            value = sk.extract(row)
            is_none = value is None
            # Represent None ordering: (1, None) sorts after real values when nulls_last
            none_flag = 1 if (is_none and nulls_last) else (0 if is_none else 0)
            if not is_none:
                # Invert value for descending sort by wrapping in a negation-safe tuple
                sort_val = (none_flag, not sk.ascending, value)
            else:
                sort_val = (none_flag, not sk.ascending, "")
            parts.append(sort_val)
        return tuple(parts)

    return _key


def sort_table(
    rows: List[Dict[str, Any]], options: SortOptions
) -> List[Dict[str, Any]]:
    """Return a new sorted list of rows according to SortOptions."""
    if not options.keys:
        return list(rows)
    key_fn = _sort_key_fn(options.keys, options.nulls_last)
    return sorted(rows, key=key_fn)


def sort_dataset(
    dataset: Dict[str, List[Dict[str, Any]]],
    table_options: Dict[str, SortOptions],
) -> Dict[str, List[Dict[str, Any]]]:
    """Sort each table in a dataset using per-table SortOptions.

    Tables not present in *table_options* are returned unchanged.
    """
    result: Dict[str, List[Dict[str, Any]]] = {}
    for table_name, rows in dataset.items():
        opts = table_options.get(table_name)
        result[table_name] = sort_table(rows, opts) if opts else list(rows)
    return result
