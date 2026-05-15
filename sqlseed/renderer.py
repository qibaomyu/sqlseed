"""High-level rendering pipeline: schema -> generated data -> formatted output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlseed.formatter import format_dataset
from sqlseed.generator import generate_dataset
from sqlseed.schema import SchemaDefinition
from sqlseed.validator import validate_schema


@dataclass
class RenderOptions:
    """Options controlling the rendering pipeline."""

    fmt: str = "sql"
    seed: int | None = None
    validate: bool = True
    tables: list[str] = field(default_factory=list)


@dataclass
class RenderResult:
    """Holds the output of a render pass."""

    outputs: dict[str, str] = field(default_factory=dict)
    dataset: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def render(
    schema: SchemaDefinition,
    options: RenderOptions | None = None,
) -> RenderResult:
    """Run the full pipeline: validate -> generate -> format.

    Returns a :class:`RenderResult` with formatted output strings and the raw
    dataset so callers can inspect or persist the data however they like.
    """
    if options is None:
        options = RenderOptions()

    result = RenderResult()

    # --- validation ---
    if options.validate:
        validation = validate_schema(schema)
        if not validation.is_valid:
            result.errors = [str(e) for e in validation.errors]
            return result

    # --- table filtering ---
    tables_to_render = {
        t.name: t
        for t in schema.tables
        if not options.tables or t.name in options.tables
    }

    # --- generation ---
    from sqlseed.schema import SchemaDefinition as SD

    filtered_schema = SD(tables=list(tables_to_render.values()))
    result.dataset = generate_dataset(filtered_schema)

    # --- formatting (skip for sql; handled by exporter) ---
    if options.fmt != "sql":
        result.outputs = format_dataset(tables_to_render, result.dataset, options.fmt)

    return result
