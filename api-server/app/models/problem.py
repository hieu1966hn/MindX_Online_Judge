from sqlalchemy import String, Integer, Boolean, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
import enum
from typing import List, Optional

from app.db.base import Base

class ProblemDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class ScoringMode(str, enum.Enum):
    ALL_OR_NOTHING = "all_or_nothing"  # Chỉ AC khi đúng hết 100% testcases
    PARTIAL = "partial"               # Tính điểm theo tỷ lệ testcases đúng

class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # VD: SUM2NUM
    title: Mapped[str] = mapped_column(String(255))
    difficulty: Mapped[ProblemDifficulty] = mapped_column(
        SAEnum(ProblemDifficulty), default=ProblemDifficulty.MEDIUM
    )
    
    # Nội dung bài tập
    statement_md: Mapped[Optional[str]] = mapped_column(Text)
    
    # Giới hạn kỹ thuật
    time_limit_ms: Mapped[int] = mapped_column(Integer, default=1000)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=256)
    
    # Cấu hình chấm bài
    scoring_mode: Mapped[ScoringMode] = mapped_column(
        SAEnum(ScoringMode), default=ScoringMode.ALL_OR_NOTHING
    )
    allowed_languages: Mapped[str] = mapped_column(Text, default="c++,python") # Lưu dạng comma-separated
    
    # Metadata & Filesystem
    package_path: Mapped[Optional[str]] = mapped_column(String(512)) # Path tới problem-packages/
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_by: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Problem {self.code}: {self.title}>"
