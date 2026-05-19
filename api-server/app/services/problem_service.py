"""
Problem service layer — business logic for problem management.
"""
from pathlib import Path
from typing import Optional
import yaml

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.problem import Problem
from app.schemas.problem import ProblemCreate, ProblemUpdate, ProblemYaml
from app.core.config import settings


def create_problem(data: ProblemCreate, created_by: str, db: Session) -> Problem:
    """
    Create a new problem record.
    
    Args:
        data: Problem creation data
        created_by: User ID of creator
        db: Database session
        
    Returns:
        Created Problem instance
    """
    import uuid
    from datetime import datetime, timezone
    
    problem = Problem(
        id=str(uuid.uuid4()),
        code=data.code,
        title=data.title,
        statement_md=data.statement_md,
        time_limit_ms=data.time_limit_ms,
        memory_limit_mb=data.memory_limit_mb,
        scoring_mode=data.scoring_mode,
        allowed_languages=",".join(data.allowed_languages),
        package_path=data.package_path,
        is_visible=data.is_visible,
        is_archived=False,
        created_by=created_by,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


def get_problem(problem_id: str, db: Session) -> Optional[Problem]:
    """Get a problem by ID."""
    return db.execute(
        select(Problem).where(Problem.id == problem_id)
    ).scalar_one_or_none()


def get_problem_by_code(code: str, db: Session) -> Optional[Problem]:
    """Get a problem by code."""
    return db.execute(
        select(Problem).where(Problem.code == code)
    ).scalar_one_or_none()


def list_problems(db: Session, visible_only: bool = True, include_archived: bool = False) -> list[Problem]:
    """
    List problems with optional filters.
    
    Args:
        db: Database session
        visible_only: If True, only return visible problems
        include_archived: If True, include archived problems
        
    Returns:
        List of Problem instances
    """
    query = select(Problem)
    
    if visible_only:
        query = query.where(Problem.is_visible == True)
    
    if not include_archived:
        query = query.where(Problem.is_archived == False)
    
    query = query.order_by(Problem.created_at.desc())
    
    return list(db.execute(query).scalars().all())


def update_problem(problem_id: str, data: ProblemUpdate, db: Session) -> Optional[Problem]:
    """
    Update a problem with partial data.
    
    Args:
        problem_id: Problem ID
        data: Partial update data
        db: Database session
        
    Returns:
        Updated Problem instance or None if not found
    """
    from datetime import datetime, timezone
    
    problem = get_problem(problem_id, db)
    if not problem:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    
    # Handle allowed_languages list -> comma-separated string
    if "allowed_languages" in update_data:
        update_data["allowed_languages"] = ",".join(update_data["allowed_languages"])
    
    for key, value in update_data.items():
        setattr(problem, key, value)
    
    problem.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(problem)
    return problem


def archive_problem(problem_id: str, db: Session) -> Optional[Problem]:
    """
    Archive a problem (soft delete).
    
    Args:
        problem_id: Problem ID
        db: Database session
        
    Returns:
        Archived Problem instance or None if not found
    """
    from datetime import datetime, timezone
    
    problem = get_problem(problem_id, db)
    if not problem:
        return None
    
    problem.is_archived = True
    problem.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(problem)
    return problem


def parse_problem_yaml(path: Path) -> ProblemYaml:
    """
    Parse problem.yaml file.
    
    Args:
        path: Path to problem.yaml
        
    Returns:
        Parsed ProblemYaml instance
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If YAML is invalid or missing required fields
    """
    if not path.exists():
        raise FileNotFoundError(f"problem.yaml not found at {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    try:
        return ProblemYaml(**data)
    except Exception as e:
        raise ValueError(f"Invalid problem.yaml: {e}")


def serialize_problem_yaml(problem: ProblemYaml, path: Path) -> None:
    """
    Serialize ProblemYaml to file.
    
    Args:
        problem: ProblemYaml instance
        path: Path to write problem.yaml
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(problem.model_dump(), f, default_flow_style=False, allow_unicode=True)
