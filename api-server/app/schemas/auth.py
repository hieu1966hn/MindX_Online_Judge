"""
Pydantic V2 schemas for authentication.

Schemas:
- LoginRequest   — credentials submitted by the user
- TokenResponse  — JWT access token returned after successful login
- TokenPayload   — decoded JWT claims (used internally for validation)
"""
from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class LoginRequest(BaseModel):
    """Credentials submitted to POST /api/v1/auth/login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Returned to the client after a successful login."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Decoded JWT payload.

    Fields:
    - sub  : user id (UUID string)
    - role : UserRole of the authenticated user
    - jti  : JWT ID — used for token blacklisting on logout (MVP: in-memory set)
    - exp  : expiry timestamp (Unix epoch seconds)
    """

    sub: str        # user id
    role: UserRole
    jti: str        # JWT ID for blacklisting
    exp: int
