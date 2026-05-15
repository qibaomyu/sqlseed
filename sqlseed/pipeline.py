"""Pipeline: wire together generate → sample → render in one call."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from sqlseed.generator import generate_dataset
from sqlseed.renderer import RenderOptions, RenderResult, render
from sqlseed.sampler import SampleOptions, sample_dataset
from sqlseed.schema import SchemaDefinition
from sqlseed.validator import validate_schema


@dataclass
class PipelineOptions:
    """Top-level options for a full seed pipeline run."""

    render: RenderOptions = field(default_factory=RenderOptions)
    sample: Optional[SampleOptions] = None
    validate: bool = True


def run_pipeline(
    schema: SchemaDefinition,
    options: Optional[PipelineOptions] = None,
) -> RenderResult:
    """Execute the full seeding pipeline and return a :class:`RenderResult`.

    Steps
    -----
    1. Optionally validate the schema.
    2. Generate rows for every table.
    3. Optionally sample the generated rows.
    4. Render to the requested output format.
    """
    if options is None:
        options = PipelineOptions()

    # 1. Validate
    if options.validate:
        result = validate_schema(schema)
        if not result.ok:
            # Return an error result without generating data
            from sqlseed.renderer import RenderResult
            return RenderResult(errors=[str(e) for e in result.errors], output={})

    # 2. Generate
    dataset: Dict[str, List[Dict]] = generate_dataset(schema)

    # 3. Sample (optional)
    if options.sample is not None:
        dataset = sample_dataset(dataset, schema.tables, options.sample)

    # 4. Render
    return render(schema, dataset, options.render)
