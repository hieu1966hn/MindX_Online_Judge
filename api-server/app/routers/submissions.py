"""
Submission endpoints for MindX Online Judge.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionRead
from app.services import submission_service

router = APIRouter()

ALL_ROLES = (
    UserRole.STUDENT,
    UserRole.TEACHER,
    UserRole.ADMIN,
    UserRole.SUPER_ADMIN,
)
TEACHER_ROLES = (UserRole.TEACHER, UserRole.ADMIN, UserRole.SUPER_ADMIN)


@router.get("/", response_model=list[SubmissionRead])
def list_my_submissions(
    current_user: User = Depends(require_role(*ALL_ROLES)),
    db: Session = Depends(get_db),
) -> list[Submission]:
    return submission_service.list_submissions_for_user(current_user.id, db)


@router.post("/", response_model=SubmissionRead, status_code=status.HTTP_201_CREATED)
def create_submission(
    data: SubmissionCreate,
    current_user: User = Depends(require_role(*ALL_ROLES)),
    db: Session = Depends(get_db),
) -> Submission:
    submission = submission_service.create_submission(data, current_user.id, db)
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )
    return submission


@router.get("/{submission_id}", response_model=SubmissionRead)
def get_submission(
    submission_id: str,
    current_user: User = Depends(require_role(*ALL_ROLES)),
    db: Session = Depends(get_db),
) -> Submission:
    submission = submission_service.get_submission(submission_id, db)
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    is_teacher = current_user.role in TEACHER_ROLES
    if submission.user_id != current_user.id and not is_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this submission",
        )

    return submission
