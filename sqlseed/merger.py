"""Merge multiple datasets into a single unified dataset."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

Row = Dict[str, object]
Dataset = Dict[str, List[Row]]


@dataclass
class MergeOptions:
    """Options controlling how datasets are merged."""

    deduplicate: bool = False
    dedup_key: Optional[str] = None
    fill_missing: bool = True
    fill_value: object = None

    def __post_init__(self) -> None:
        if self.deduplicate and self.dedup_key is None:
            raise ValueError("dedup_key must be set when deduplicate is True")


def _dedup_rows(rows: List[Row], key: str) -> List[Row]:
    """Return rows with duplicates removed, keeping the first occurrence."""
    seen = set()
    result: List[Row] = []
    for row in rows:
        k = row.get(key)
        if k not in seen:
            seen.add(k)
            result.append(row)
    return result


def _unify_keys(rows: List[Row], fill_value: object) -> List[Row]:
    """Ensure every row in *rows* has the same set of keys."""
    all_keys: set = set()
    for row in rows:
        all_keys.update(row.keys())
    return [{k: row.get(k, fill_value) for k in all_keys} for row in rows]


def merge_datasets(datasets: List[Dataset], options: Optional[MergeOptions] = None) -> Dataset:
    """Merge a list of datasets into one.

    Tables present in multiple datasets have their rows concatenated.
    Tables present in only one dataset are included as-is.
    """
    if options is None:
        options = MergeOptions()

    merged: Dataset = {}

    for dataset in datasets:
        for table_name, rows in dataset.items():
            merged.setdefault(table_name, []).extend(rows)

    if options.fill_missing:
        merged = {name: _unify_keys(rows, options.fill_value) for name, rows in merged.items()}

    if options.deduplicate:
        merged = {
            name: _dedup_rows(rows, options.dedup_key)  # type: ignore[arg-type]
            for name, rows in merged.items()
        }

    return merged
