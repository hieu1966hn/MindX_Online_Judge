"""
Submission service layer — create submissions and run judge.
"""
from datetime import datetime, timezone
import uuid
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.submission import Submission
from app.models.problem import Problem
from app.schemas.submission import SubmissionCreate
from app.judge.local_runner import LocalRunner
from app.judge.base import JudgeStatus


def create_submission(data: SubmissionCreate, user_id: str, db: Session) -> Optional[Submission]:
    """
    Create a submission, run judge synchronously, and store result.
    MVP behavior: compares output against placeholder expected output if available later.
    """
    problem = db.execute(
        select(Problem).where(Problem.id == data.problem_id)
    ).scalar_one_or_none()
    if problem is None:
        return None

    submission = Submission(
        id=str(uuid.uuid4()),
        problem_id=data.problem_id,
        user_id=user_id,
        language=data.language,
        source_code=data.source_code,
        status=JudgeStatus.RUNNING,
        created_at=datetime.now(timezone.utc),
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    runner = LocalRunner()
    result = runner.run(
        source_code=data.source_code,
        language=data.language,
        input_data="",
        time_limit_ms=problem.time_limit_ms,
        memory_limit_mb=problem.memory_limit_mb,
    )

    submission.status = result.status
    submission.time_ms = result.time_ms
    submission.memory_mb = result.memory_mb
    submission.message = result.message
    submission.judged_at = datetime.now(timezone.utc)

    if result.status == JudgeStatus.ACCEPTED:
        submission.score = 100.0
    else:
        submission.score = 0.0

    db.commit()
    db.refresh(submission)
    return submission


def get_submission(submission_id: str, db: Session) -> Optional[Submission]:
    return db.execute(
        select(Submission).where(Submission.id == submission_id)
    ).scalar_one_or_none()


def list_submissions_for_user(user_id: str, db: Session) -> list[Submission]:
    return list(
        db.execute(
            select(Submission)
            .where(Submission.user_id == user_id)
            .order_by(Submission.created_at.desc())
        ).scalars().all()
    )


def list_submissions_for_problem(problem_id: str, db: Session) -> list[Submission]:
    return list(
        db.execute(
            select(Submission)
            .where(Submission.problem_id == problem_id)
            .order_by(Submission.created_at.desc())
        ).scalars().all()
    )
