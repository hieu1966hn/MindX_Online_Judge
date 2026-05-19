"""
Pydantic V2 schemas for Submission resources.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.judge.base import JudgeStatus


class SubmissionCreate(BaseModel):
    """Used when a student submits a solution."""
    problem_id: str
    language: str = Field(max_length=50)
    source_code: str = Field(min_length=1)


class SubmissionRead(BaseModel):
    """Returned by the API; maps directly from the ORM Submission object."""
    id: str
    problem_id: str
    user_id: str
    language: str
    source_code: str
    status: JudgeStatus
    score: float
    time_ms: int
    memory_mb: float
    message: Optional[str] = None
    created_at: datetime
    judged_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
