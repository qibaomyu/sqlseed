"""Row-level data transformation pipeline for sqlseed datasets."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

Row = Dict[str, Any]
Dataset = Dict[str, List[Row]]
TransformFn = Callable[[Row], Row]


@dataclass
class ColumnTransform:
    """Applies a transformation function to a specific column in every row."""

    column: str
    fn: Callable[[Any], Any]

    def apply(self, row: Row) -> Row:
        if self.column in row:
            row = dict(row)
            row[self.column] = self.fn(row[self.column])
        return row


@dataclass
class TableTransformer:
    """Holds an ordered list of transforms applied to rows of a single table."""

    table_name: str
    transforms: List[TransformFn] = field(default_factory=list)

    def add(self, transform: TransformFn) -> "TableTransformer":
        self.transforms.append(transform)
        return self

    def apply(self, rows: List[Row]) -> List[Row]:
        result = []
        for row in rows:
            for transform in self.transforms:
                row = transform(row)
            result.append(row)
        return result


@dataclass
class TransformOptions:
    """Configuration for dataset-level transformation."""

    transformers: Dict[str, TableTransformer] = field(default_factory=dict)

    def add_transformer(self, transformer: TableTransformer) -> "TransformOptions":
        self.transformers[transformer.table_name] = transformer
        return self


def transform_dataset(dataset: Dataset, options: Optional[TransformOptions] = None) -> Dataset:
    """Apply registered transformers to matching tables in a dataset."""
    if options is None or not options.transformers:
        return dataset

    result: Dataset = {}
    for table_name, rows in dataset.items():
        transformer = options.transformers.get(table_name)
        if transformer is not None:
            result[table_name] = transformer.apply(rows)
        else:
            result[table_name] = rows
    return result
