"""
Pydantic V2 schemas for User resources.

Schemas:
- UserBase      — shared fields (name, email, role)
- UserCreate    — extends UserBase with password for account creation
- UserRead      — extends UserBase with server-assigned fields; ORM-compatible
- UserUpdate    — all fields optional for partial PATCH updates
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    """Used when creating a new user account (Admin action)."""

    password: str = Field(min_length=8)


class UserRead(UserBase):
    """Returned by the API; maps directly from the ORM User object."""

    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """All fields are optional — supports partial PATCH updates."""

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8)
