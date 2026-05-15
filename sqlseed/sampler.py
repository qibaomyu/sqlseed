"""Sampler module: draw reproducible subsets of generated rows."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from sqlseed.schema import TableDefinition


@dataclass
class SampleOptions:
    """Options controlling how rows are sampled from a dataset."""

    fraction: Optional[float] = None   # e.g. 0.5 → 50 % of rows
    n: Optional[int] = None            # exact number of rows
    seed: Optional[int] = None         # for reproducibility
    shuffle: bool = True               # shuffle before slicing

    def __post_init__(self) -> None:
        if self.fraction is not None and not (0.0 < self.fraction <= 1.0):
            raise ValueError("fraction must be in (0, 1]")
        if self.n is not None and self.n < 0:
            raise ValueError("n must be a non-negative integer")
        if self.fraction is not None and self.n is not None:
            raise ValueError("Specify either fraction or n, not both")


def sample_table(
    rows: List[Dict],
    table: TableDefinition,
    options: SampleOptions,
) -> List[Dict]:
    """Return a sampled subset of *rows* according to *options*."""
    rng = random.Random(options.seed)

    working = list(rows)
    if options.shuffle:
        rng.shuffle(working)

    if options.fraction is not None:
        count = max(1, int(len(working) * options.fraction))
    elif options.n is not None:
        count = min(options.n, len(working))
    else:
        count = len(working)

    return working[:count]


def sample_dataset(
    dataset: Dict[str, List[Dict]],
    tables: List[TableDefinition],
    options: SampleOptions,
) -> Dict[str, List[Dict]]:
    """Apply sampling to every table in *dataset*."""
    table_map = {t.name: t for t in tables}
    return {
        name: sample_table(rows, table_map[name], options)
        for name, rows in dataset.items()
        if name in table_map
    }
