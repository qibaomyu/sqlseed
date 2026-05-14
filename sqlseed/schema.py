"""Schema definition models for sqlseed."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


VALID_COLUMN_TYPES = {
    "integer",
    "float",
    "string",
    "text",
    "boolean",
    "date",
    "datetime",
    "uuid",
    "email",
    "name",
    "phone",
    "address",
}


@dataclass
class ColumnDefinition:
    name: str
    type: str
    nullable: bool = False
    unique: bool = False
    primary_key: bool = False
    foreign_key: Optional[str] = None  # e.g. "users.id"
    default: Optional[Any] = None
    constraints: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.type not in VALID_COLUMN_TYPES:
            raise ValueError(
                f"Invalid column type '{self.type}'. "
                f"Must be one of: {sorted(VALID_COLUMN_TYPES)}"
            )


@dataclass
class TableDefinition:
    name: str
    columns: List[ColumnDefinition]
    row_count: int = 10

    def __post_init__(self):
        if self.row_count < 1:
            raise ValueError(f"row_count must be >= 1, got {self.row_count}")
        names = [col.name for col in self.columns]
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate column names in table '{self.name}'")

    def get_column(self, name: str) -> Optional[ColumnDefinition]:
        for col in self.columns:
            if col.name == name:
                return col
        return None


@dataclass
class SchemaDefinition:
    tables: List[TableDefinition]

    def get_table(self, name: str) -> Optional[TableDefinition]:
        for table in self.tables:
            if table.name == name:
                return table
        return None

    def table_names(self) -> List[str]:
        return [t.name for t in self.tables]
