"""Demonstrate the sqlseed pipeline with sampling.

Run from the project root::

    python examples/pipeline_demo.py
"""

from __future__ import annotations

import json
import pathlib

from sqlseed.pipeline import PipelineOptions, run_pipeline
from sqlseed.renderer import RenderOptions
from sqlseed.sampler import SampleOptions
from sqlseed.schema_loader import load_schema_from_yaml

SCHEMA_PATH = pathlib.Path(__file__).parent / "sample_schema.yaml"


def main() -> None:
    schema = load_schema_from_yaml(str(SCHEMA_PATH))

    # Full generation, JSON output
    full_opts = PipelineOptions(render=RenderOptions(format="json"))
    full_result = run_pipeline(schema, full_opts)

    if not full_result.ok:
        print("Validation errors:")
        for err in full_result.errors:
            print(" -", err)
        return

    print("=== Full dataset ===")
    for table_name, content in full_result.output.items():
        rows = json.loads(content) if isinstance(content, str) else content
        print(f"  {table_name}: {len(rows)} rows")

    # Sampled generation — 30 % of each table, reproducible
    sampled_opts = PipelineOptions(
        render=RenderOptions(format="json"),
        sample=SampleOptions(fraction=0.3, seed=99),
    )
    sampled_result = run_pipeline(schema, sampled_opts)

    print("\n=== Sampled dataset (30 %) ===")
    for table_name, content in sampled_result.output.items():
        rows = json.loads(content) if isinstance(content, str) else content
        print(f"  {table_name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
