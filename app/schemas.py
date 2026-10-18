from pydantic import BaseModel, Field
from typing import Any

class TransformRequest(BaseModel):
    operations: list[str] = Field(default_factory=list, max_length=8)
    drop_duplicates: bool = True
    missing_strategy: str = Field(default="keep", pattern="^(keep|drop_rows|fill_empty)$")
    filter_column: str | None = None
    filter_contains: str | None = None

class AIRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    columns: list[str] = Field(default_factory=list, max_length=100)
    sample_rows: list[dict[str, Any]] = Field(default_factory=list, max_length=5)
    quality_summary: dict[str, Any] = Field(default_factory=dict)
    goal: str = Field(min_length=5, max_length=1000)
