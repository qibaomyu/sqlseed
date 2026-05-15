"""Demonstrates using TableFilter to post-process generated datasets."""

from sqlseed.schema_loader import load_schema_from_dict
from sqlseed.generator import generate_dataset
from sqlseed.filter import TableFilter, filter_dataset


SCHEMA_DICT = {
    "tables": [
        {
            "name": "users",
            "row_count": 20,
            "columns": [
                {"name": "id", "type": "integer", "primary_key": True},
                {"name": "username", "type": "string", "max_length": 12},
                {"name": "age", "type": "integer"},
                {"name": "active", "type": "boolean"},
            ],
        }
    ]
}


def main():
    schema = load_schema_from_dict(SCHEMA_DICT)
    dataset = generate_dataset(schema)

    print(f"Total users generated: {len(dataset['users'])}")

    # Keep only adult active users
    user_filter = (
        TableFilter("users")
        .add("age", lambda v: v is not None and v >= 18, "adult")
        .add("active", lambda v: v is True, "active only")
    )

    filtered = filter_dataset(dataset, {"users": user_filter})
    print(f"Adult active users: {len(filtered['users'])}")

    for row in filtered["users"][:3]:
        print(f"  id={row['id']}  username={row['username']}  age={row['age']}  active={row['active']}")


if __name__ == "__main__":
    main()
