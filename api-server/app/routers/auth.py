"""
Authentication endpoints for MindX Online Judge.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.deps import blacklist_token, get_current_user, oauth2_scheme
from app.core.rate_limit import (
    check_login_rate_limit,
    record_login_attempt,
    reset_login_attempts,
)
from app.core.security import create_access_token, decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth_service

# Note: Prefix /api/v1/auth is handled in main.py
router = APIRouter()


class PasswordResetRequestSchema(BaseModel):
    email: EmailStr


class PasswordResetConfirmSchema(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    client_ip = request.client.host if request.client else "unknown"
    check_login_rate_limit(client_ip)

    user = auth_service.authenticate_user(credentials.email, credentials.password, db)
    if user is None:
        record_login_attempt(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        data={
            "sub": user.id,
            "role": user.role.value,
        }
    )
    reset_login_attempts(client_ip)
    return TokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Logout by blacklisting the current token's JTI.
    """
    payload = decode_access_token(token)
    jti = payload.get("jti")
    if jti:
        blacklist_token(jti)


@router.post("/password-reset/request")
def request_password_reset(
    data: PasswordResetRequestSchema,
    db: Session = Depends(get_db),
) -> dict:
    user = auth_service.get_user_by_email(data.email, db)
    if user:
        auth_service.create_password_reset_token(user.id, db)
    
    return {
        "message": "If the email exists, a password reset link has been sent. Please check your inbox."
    }


@router.post("/password-reset/confirm")
def confirm_password_reset(
    data: PasswordResetConfirmSchema,
    db: Session = Depends(get_db),
) -> dict:
    success = auth_service.confirm_password_reset(
        data.token, data.new_password, db
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    return {"message": "Password has been reset successfully"}
