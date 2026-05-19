"""
User management endpoints for MindX Online Judge.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import auth_service

# Note: Prefix /api/v1/users is handled in main.py
router = APIRouter()


ADMIN_ROLES = (UserRole.ADMIN, UserRole.SUPER_ADMIN)
ALL_ROLES = (
    UserRole.STUDENT,
    UserRole.TEACHER,
    UserRole.ADMIN,
    UserRole.SUPER_ADMIN,
)


def _ensure_can_assign_role(actor: User, role: UserRole | None) -> None:
    """Prevent Admin users from assigning or escalating to Super Admin."""
    if role == UserRole.SUPER_ADMIN and actor.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Super Admin can assign the Super Admin role",
        )


@router.get("/me", response_model=UserRead)
def get_me(
    current_user: User = Depends(require_role(*ALL_ROLES)),
) -> User:
    return current_user


@router.get("/", response_model=list[UserRead])
def list_users(
    current_user: User = Depends(require_role(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    current_user: User = Depends(require_role(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
) -> User:
    _ensure_can_assign_role(current_user, data.role)

    existing = auth_service.get_user_by_email(data.email, db)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    return auth_service.create_user(data, db)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: str,
    current_user: User = Depends(require_role(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
) -> User:
    user = auth_service.get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    data: UserUpdate,
    current_user: User = Depends(require_role(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
) -> User:
    user = auth_service.get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    _ensure_can_assign_role(current_user, data.role)

    if data.email is not None and data.email != user.email:
        existing = auth_service.get_user_by_email(data.email, db)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )
        user.email = data.email

    if data.name is not None:
        user.name = data.name
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password is not None:
        user.password_hash = hash_password(data.password)

    db.commit()
    db.refresh(user)
    return user
