"""
SQLAlchemy ORM model for Submission.
"""
from sqlalchemy import String, Integer, Float, Text, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime

from app.db.base import Base
from app.judge.base import JudgeStatus


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    
    # Foreign keys
    problem_id: Mapped[str] = mapped_column(String(36), ForeignKey("problems.id"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    
    # Submission details
    language: Mapped[str] = mapped_column(String(50))
    source_code: Mapped[str] = mapped_column(Text)
    
    # Judge results
    status: Mapped[JudgeStatus] = mapped_column(
        SAEnum(JudgeStatus), 
        default=JudgeStatus.PENDING,
        index=True
    )
    score: Mapped[float] = mapped_column(Float, default=0.0)
    time_ms: Mapped[int] = mapped_column(Integer, default=0)
    memory_mb: Mapped[float] = mapped_column(Float, default=0.0)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    judged_at: Mapped[datetime] = mapped_column(nullable=True)

    def __repr__(self):
        return f"<Submission {self.id}: {self.status}>"
