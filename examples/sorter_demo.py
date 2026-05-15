"""Demonstration of sqlseed dataset sorting."""

from sqlseed.sorter import SortKey, SortOptions, sort_dataset


def main() -> None:
    # Simulate a small generated dataset
    dataset = {
        "users": [
            {"id": 3, "username": "charlie", "score": 70},
            {"id": 1, "username": "alice", "score": 95},
            {"id": 5, "username": "eve", "score": None},
            {"id": 2, "username": "bob", "score": 80},
            {"id": 4, "username": "dave", "score": 60},
        ],
        "orders": [
            {"order_id": 102, "user_id": 3, "amount": 49.99},
            {"order_id": 101, "user_id": 1, "amount": 120.00},
            {"order_id": 103, "user_id": 2, "amount": 9.99},
        ],
    }

    # Sort users by score descending, then username ascending
    user_opts = SortOptions(
        keys=[
            SortKey(column="score", ascending=False),
            SortKey(column="username", ascending=True),
        ],
        nulls_last=True,
    )

    # Sort orders by amount ascending
    order_opts = SortOptions(
        keys=[SortKey(column="amount", ascending=True)]
    )

    sorted_data = sort_dataset(
        dataset,
        table_options={"users": user_opts, "orders": order_opts},
    )

    print("=== Sorted Users (score DESC, username ASC, nulls last) ===")
    for row in sorted_data["users"]:
        score_display = row["score"] if row["score"] is not None else "NULL"
        print(f"  id={row['id']}  username={row['username']:<10} score={score_display}")

    print()
    print("=== Sorted Orders (amount ASC) ===")
    for row in sorted_data["orders"]:
        print(f"  order_id={row['order_id']}  user_id={row['user_id']}  amount={row['amount']:.2f}")


if __name__ == "__main__":
    main()
