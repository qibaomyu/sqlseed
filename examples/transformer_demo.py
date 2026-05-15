"""Demonstrates the transformer module integrated with the pipeline."""

from sqlseed.schema_loader import load_schema_from_dict
from sqlseed.pipeline import PipelineOptions, run_pipeline
from sqlseed.transformer import ColumnTransform, TableTransformer, TransformOptions
from sqlseed.renderer import RenderOptions


SCHEMA_DICT = {
    "tables": [
        {
            "name": "users",
            "row_count": 6,
            "columns": [
                {"name": "id", "type": "integer", "primary_key": True},
                {"name": "username", "type": "string"},
                {"name": "email", "type": "email"},
                {"name": "score", "type": "integer"},
            ],
        }
    ]
}


def main() -> None:
    schema = load_schema_from_dict(SCHEMA_DICT)

    # Mask emails and cap scores at 100
    email_mask = ColumnTransform(column="email", fn=lambda _: "redacted@example.com")
    score_cap = ColumnTransform(column="score", fn=lambda v: min(v, 100) if isinstance(v, int) else v)

    tt = TableTransformer("users")
    tt.add(email_mask.apply)
    tt.add(score_cap.apply)

    transform_opts = TransformOptions()
    transform_opts.add_transformer(tt)

    pipeline_opts = PipelineOptions(
        render_options=RenderOptions(format="json"),
        transform_options=transform_opts,
    )

    result = run_pipeline(schema, pipeline_opts)

    if not result.ok:
        print("Pipeline errors:")
        for err in result.errors:
            print(f"  - {err}")
        return

    print("Transformed users:")
    for row in result.dataset.get("users", []):
        print(f"  id={row['id']}  username={row['username']}  email={row['email']}  score={row['score']}")


if __name__ == "__main__":
    main()
