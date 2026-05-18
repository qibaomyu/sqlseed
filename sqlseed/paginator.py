"""Paginator: split dataset rows into pages for chunked output or processing."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Iterator


@dataclass
class PaginationOptions:
    page_size: int = 100
    start_page: int = 1

    def __post_init__(self) -> None:
        if self.page_size < 1:
            raise ValueError("page_size must be at least 1")
        if self.start_page < 1:
            raise ValueError("start_page must be at least 1")


@dataclass
class Page:
    table: str
    page_number: int
    rows: List[Dict[str, Any]]

    @property
    def size(self) -> int:
        return len(self.rows)

    def __str__(self) -> str:
        return f"Page(table={self.table!r}, page={self.page_number}, rows={self.size})"


@dataclass
class PaginatedTable:
    table: str
    pages: List[Page] = field(default_factory=list)

    @property
    def total_rows(self) -> int:
        return sum(p.size for p in self.pages)

    @property
    def page_count(self) -> int:
        return len(self.pages)

    def __iter__(self) -> Iterator[Page]:
        return iter(self.pages)


def paginate_table(
    table: str,
    rows: List[Dict[str, Any]],
    options: PaginationOptions,
) -> PaginatedTable:
    """Split *rows* for *table* into fixed-size pages."""
    result = PaginatedTable(table=table)
    page_number = options.start_page
    for offset in range(0, max(len(rows), 1), options.page_size):
        chunk = rows[offset : offset + options.page_size]
        if not chunk and rows:
            break
        result.pages.append(Page(table=table, page_number=page_number, rows=chunk))
        page_number += 1
    return result


def paginate_dataset(
    dataset: Dict[str, List[Dict[str, Any]]],
    options: PaginationOptions,
) -> Dict[str, PaginatedTable]:
    """Paginate every table in *dataset*."""
    return {
        table: paginate_table(table, rows, options)
        for table, rows in dataset.items()
    }
