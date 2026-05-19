"""
Pydantic V2 schemas for Problem resources.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProblemYaml(BaseModel):
    """
    Schema for problem.yaml file structure.
    
    Used for parsing and serializing problem package metadata.
    """
    code: str
    title: str
    time_limit_ms: int = Field(ge=100)
    memory_limit_mb: int = Field(ge=1)
    allowed_languages: list[str]
    scoring_mode: str = "all_or_nothing"


class ProblemBase(BaseModel):
    """Shared fields for Problem resources."""
    code: str = Field(max_length=100)
    title: str = Field(max_length=255)
    statement_md: str = ""
    time_limit_ms: int = Field(ge=100, default=1000)
    memory_limit_mb: int = Field(ge=1, default=256)
    allowed_languages: list[str] = Field(default_factory=lambda: ["python3"])
    scoring_mode: str = "all_or_nothing"
    is_visible: bool = True


class ProblemCreate(ProblemBase):
    """Used when creating a new problem (Teacher action)."""
    package_path: str


class ProblemRead(ProblemBase):
    """Returned by the API; maps directly from the ORM Problem object."""
    id: str
    is_archived: bool
    package_path: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProblemUpdate(BaseModel):
    """All fields are optional — supports partial PATCH updates."""
    title: Optional[str] = Field(default=None, max_length=255)
    statement_md: Optional[str] = None
    time_limit_ms: Optional[int] = Field(default=None, ge=100)
    memory_limit_mb: Optional[int] = Field(default=None, ge=1)
    allowed_languages: Optional[list[str]] = None
    scoring_mode: Optional[str] = None
    is_visible: Optional[bool] = None
