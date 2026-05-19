"""
SQLAlchemy ORM model for programming problems.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Problem(Base):
    """Problem metadata stored in SQLite for the local-first MVP."""

    __tablename__ = "problems"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    statement_md: Mapped[str] = mapped_column(Text, nullable=False, default="")
    time_limit_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, nullable=False, default=256)
    allowed_languages: Mapped[str] = mapped_column(Text, nullable=False, default='["python3"]')
    scoring_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="all_or_nothing")
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    package_path: Mapped[str] = mapped_column(String(500), nullable=False)
    created_by: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
