"""Demonstrate merging two generated datasets with MergeOptions."""

from sqlseed.merger import MergeOptions, merge_datasets
from sqlseed.schema import ColumnDefinition, TableDefinition, SchemaDefinition
from sqlseed.generator import generate_dataset


def _make_schema(row_count: int) -> SchemaDefinition:
    cols = [
        ColumnDefinition(name="id", type="integer", primary_key=True),
        ColumnDefinition(name="username", type="string", max_length=20),
        ColumnDefinition(name="email", type="string", max_length=40, nullable=True),
    ]
    table = TableDefinition(name="users", row_count=row_count, columns=cols)
    return SchemaDefinition(tables=[table])


def main() -> None:
    schema_a = _make_schema(5)
    schema_b = _make_schema(5)

    dataset_a = generate_dataset(schema_a)
    dataset_b = generate_dataset(schema_b)

    print("=== Dataset A ===")
    for row in dataset_a["users"]:
        print(" ", row)

    print("\n=== Dataset B ===")
    for row in dataset_b["users"]:
        print(" ", row)

    # Merge with deduplication on 'id'
    opts = MergeOptions(deduplicate=True, dedup_key="id", fill_missing=True)
    merged = merge_datasets([dataset_a, dataset_b], opts)

    print(f"\n=== Merged ({len(merged['users'])} rows) ===")
    for row in merged["users"]:
        print(" ", row)


if __name__ == "__main__":
    main()
