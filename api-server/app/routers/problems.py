"""
Problem management endpoints for MindX Online Judge.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.problem import Problem
from app.schemas.problem import ProblemCreate, ProblemRead, ProblemUpdate
from app.services import problem_service

# Note: Prefix /api/v1/problems is handled in main.py
router = APIRouter()

TEACHER_ROLES = (UserRole.TEACHER, UserRole.ADMIN, UserRole.SUPER_ADMIN)
STUDENT_ROLES = (UserRole.STUDENT, UserRole.TEACHER, UserRole.ADMIN, UserRole.SUPER_ADMIN)

@router.get("/", response_model=List[ProblemRead])
def list_problems(
    current_user: User = Depends(require_role(*STUDENT_ROLES)),
    db: Session = Depends(get_db),
) -> List[Problem]:
    """
    Get list of available problems.
    Students only see visible, non-archived problems.
    Teachers+ see everything.
    """
    is_teacher = current_user.role in TEACHER_ROLES
    return problem_service.list_problems(
        db, 
        visible_only=not is_teacher,
        include_archived=is_teacher
    )

@router.post("/", response_model=ProblemRead, status_code=status.HTTP_201_CREATED)
def create_problem(
    data: ProblemCreate,
    current_user: User = Depends(require_role(*TEACHER_ROLES)),
    db: Session = Depends(get_db),
) -> Problem:
    """Create a new problem (Teacher+)."""
    # Check if code already exists
    existing = problem_service.get_problem_by_code(data.code, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Problem with code '{data.code}' already exists"
        )
    
    return problem_service.create_problem(data, current_user.id, db)

@router.get("/{problem_id}", response_model=ProblemRead)
def get_problem(
    problem_id: str,
    current_user: User = Depends(require_role(*STUDENT_ROLES)),
    db: Session = Depends(get_db),
) -> Problem:
    """Get detailed problem information."""
    problem = problem_service.get_problem(problem_id, db)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
    
    # Permission check for hidden/archived problems
    is_teacher = current_user.role in TEACHER_ROLES
    if not is_teacher:
        if not problem.is_visible or problem.is_archived:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this problem"
            )
            
    return problem

@router.patch("/{problem_id}", response_model=ProblemRead)
def update_problem(
    problem_id: str,
    data: ProblemUpdate,
    current_user: User = Depends(require_role(*TEACHER_ROLES)),
    db: Session = Depends(get_db),
) -> Problem:
    """Update problem details (Teacher+)."""
    problem = problem_service.update_problem(problem_id, data, db)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
    return problem

@router.delete("/{problem_id}", response_model=ProblemRead)
def archive_problem(
    problem_id: str,
    current_user: User = Depends(require_role(*TEACHER_ROLES)),
    db: Session = Depends(get_db),
) -> Problem:
    """Soft-delete a problem by archiving it (Teacher+)."""
    problem = problem_service.archive_problem(problem_id, db)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
    return problem

# TODO: Add endpoints for file uploads (statement, testcases) in Task 6.4 phase 2
