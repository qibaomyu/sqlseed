"""High-level pipeline that validates, generates, and optionally merges datasets."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from sqlseed.schema import SchemaDefinition
from sqlseed.validator import validate_schema
from sqlseed.generator import generate_dataset
from sqlseed.renderer import RenderOptions, RenderResult, render
from sqlseed.merger import MergeOptions, merge_datasets

Row = Dict[str, object]
Dataset = Dict[str, List[Row]]


@dataclass
class PipelineOptions:
    """Options forwarded through the pipeline stages."""

    render: RenderOptions = field(default_factory=RenderOptions)
    merge: Optional[MergeOptions] = None
    extra_datasets: List[Dataset] = field(default_factory=list)


def run_pipeline(schema: SchemaDefinition, options: Optional[PipelineOptions] = None) -> RenderResult:
    """Validate *schema*, generate rows, optionally merge extra datasets, and render.

    Returns a :class:`RenderResult` whose ``dataset`` is the final merged
    (or plain generated) dataset.
    """
    if options is None:
        options = PipelineOptions()

    result = render(schema, options.render)

    if not result.ok:
        return result

    if options.extra_datasets or options.merge is not None:
        all_datasets = [result.dataset] + options.extra_datasets
        merged = merge_datasets(all_datasets, options.merge)
        return RenderResult(dataset=merged, errors=result.errors)

    return result
