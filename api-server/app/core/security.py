"""
Security utilities for MindX Online Judge.

Provides:
- hash_password   — bcrypt password hashing via passlib
- verify_password — bcrypt password verification
- create_access_token — JWT HS256 token creation with jti claim
- decode_access_token — JWT decoding with HTTPException on failure

JWT payload structure:
  {
    "sub":  "<user_id>",
    "role": "<UserRole value>",
    "jti":  "<uuid4>",
    "exp":  <unix timestamp>
  }

Safety notes (per auth-implementation-patterns skill):
  - Secrets are never logged.
  - Tokens are signed with HS256 using SECRET_KEY from settings.
  - jti enables per-token revocation (MVP: in-memory blacklist in deps.py).
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the bcrypt *hashed* value."""
    return _pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        data: Payload dict — should contain at least ``sub`` (user id) and
              ``role`` (UserRole value string).  Extra keys are preserved.
        expires_delta: Override the default expiry window.  When omitted the
                       token expires after ``settings.ACCESS_TOKEN_EXPIRE_HOURS``
                       hours.

    Returns:
        Encoded JWT string (HS256).
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        **data,
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": now,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Args:
        token: Raw JWT string.

    Returns:
        Decoded payload dict.

    Raises:
        HTTPException(401): If the token is invalid, expired, or malformed.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        raise credentials_exception
