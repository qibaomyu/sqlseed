"""End-to-end pipeline orchestrating validate → generate → transform → sample → render."""

from dataclasses import dataclass, field
from typing import Optional

from sqlseed.schema import SchemaDefinition
from sqlseed.validator import validate_schema
from sqlseed.generator import generate_dataset
from sqlseed.transformer import TransformOptions, transform_dataset
from sqlseed.sampler import SampleOptions, sample_dataset
from sqlseed.renderer import RenderOptions, RenderResult, render


@dataclass
class PipelineOptions:
    """Aggregated options controlling each stage of the pipeline."""

    render_options: RenderOptions = field(default_factory=RenderOptions)
    transform_options: Optional[TransformOptions] = None
    sample_options: Optional[SampleOptions] = None


def run_pipeline(schema: SchemaDefinition, options: Optional[PipelineOptions] = None) -> RenderResult:
    """Run the full sqlseed pipeline and return a RenderResult."""
    if options is None:
        options = PipelineOptions()

    validation = validate_schema(schema)
    if not validation.ok:
        return RenderResult(errors=validation.errors, dataset={})

    dataset = generate_dataset(schema)

    if options.transform_options is not None:
        dataset = transform_dataset(dataset, options.transform_options)

    if options.sample_options is not None:
        dataset = sample_dataset(dataset, options.sample_options)

    return render(schema, dataset, options.render_options)
