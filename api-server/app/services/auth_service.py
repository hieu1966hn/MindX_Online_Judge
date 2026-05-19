"""
Authentication service for MindX Online Judge.

Provides all user-facing auth operations:
  - authenticate_user      — verify email + password, return User or None
  - create_user            — hash password, persist new User record
  - get_user_by_email      — lookup by email
  - get_user_by_id         — lookup by primary key
  - create_password_reset_token — generate & persist a one-time reset token
  - confirm_password_reset — validate token, update password, mark token used

Security notes:
  - Passwords are never stored in plain text; bcrypt via security.hash_password.
  - Reset tokens are generated with secrets.token_urlsafe(32) (~43 URL-safe chars,
    well within the 64-char column limit).
  - Tokens expire after 1 hour and are single-use (is_used flag).
  - In development the token is printed to stdout so it can be used without an
    SMTP server.  Remove / replace this log line before going to production.
"""
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.schemas.user import UserCreate

# ---------------------------------------------------------------------------
# User lookups
# ---------------------------------------------------------------------------


def get_user_by_email(email: str, db: Session) -> User | None:
    """Return the User with the given *email*, or None if not found."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(user_id: str, db: Session) -> User | None:
    """Return the User with the given *user_id* (UUID string), or None."""
    return db.query(User).filter(User.id == user_id).first()


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def authenticate_user(email: str, password: str, db: Session) -> User | None:
    """
    Verify *email* + *password* against the database.

    Returns the matching User on success, or None when the email does not
    exist or the password is incorrect.  The caller should treat both failure
    cases identically to avoid user-enumeration attacks.
    """
    user = get_user_by_email(email, db)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# ---------------------------------------------------------------------------
# User creation
# ---------------------------------------------------------------------------


def create_user(data: UserCreate, db: Session) -> User:
    """
    Persist a new User record derived from *data*.

    The plain-text password in *data.password* is hashed before storage.
    A UUID4 string is assigned as the primary key.

    Returns the newly created and refreshed User ORM object.
    """
    user = User(
        id=str(uuid.uuid4()),
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------

_RESET_TOKEN_EXPIRE_HOURS = 1


def create_password_reset_token(user_id: str, db: Session) -> str:
    """
    Generate a secure one-time password reset token for *user_id*.

    The token is persisted to the ``password_reset_tokens`` table and expires
    after 1 hour.  For development convenience the raw token is printed to
    stdout — **remove this log line before deploying to production**.

    Returns the plain token string (to be delivered to the user out-of-band,
    e.g. via email).
    """
    token = secrets.token_urlsafe(32)  # ~43 URL-safe chars
    expires_at = datetime.now(timezone.utc) + timedelta(hours=_RESET_TOKEN_EXPIRE_HOURS)

    record = PasswordResetToken(
        id=str(uuid.uuid4()),
        user_id=user_id,
        token=token,
        is_used=False,
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()

    # [DEV ONLY] Log token to console — replace with email delivery in production
    print(f"[DEV] Password reset token for {user_id}: {token}")

    return token


def confirm_password_reset(token: str, new_password: str, db: Session) -> bool:
    """
    Validate *token* and update the associated user's password.

    Steps:
      1. Look up the PasswordResetToken record by token string.
      2. Reject if not found, already used, or expired.
      3. Hash *new_password* and update the user's ``password_hash``.
      4. Mark the token as used so it cannot be replayed.
      5. Commit and return True.

    Returns True on success, False on any validation failure.
    """
    record: PasswordResetToken | None = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == token)
        .first()
    )

    if record is None:
        return False

    if record.is_used:
        return False

    now = datetime.now(timezone.utc)
    # expires_at may be stored as a naive datetime by SQLite; normalise it.
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now > expires_at:
        return False

    user = get_user_by_id(record.user_id, db)
    if user is None:
        return False

    user.password_hash = hash_password(new_password)
    record.is_used = True
    db.commit()

    return True
