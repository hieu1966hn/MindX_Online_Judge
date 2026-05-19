"""
FastAPI dependency functions for authentication and authorization.

Provides:
- oauth2_scheme          — OAuth2PasswordBearer token extractor
- blacklist_token()      — add a jti to the in-memory revocation set
- is_token_blacklisted() — check whether a jti has been revoked
- get_current_user()     — decode JWT, validate blacklist, return User ORM object
- require_role()         — factory that returns a role-checking dependency

In-memory blacklist notes:
  The MVP stores revoked JTIs in a module-level Python set protected by a
  threading.Lock.  This is sufficient for a single-process server.

  Production upgrade path: replace with Redis SET + TTL
    redis_client.setex(f"blacklist:{jti}", ttl_seconds, "1")
    is_blacklisted = redis_client.exists(f"blacklist:{jti}") > 0
  This makes revocation durable across restarts and works with multiple
  API server replicas.

Safety notes (per auth-implementation-patterns skill):
  - Tokens are never logged.
  - Secrets are read from settings, never hard-coded.
"""
import threading
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole

# ---------------------------------------------------------------------------
# OAuth2 scheme — extracts the Bearer token from the Authorization header
# ---------------------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ---------------------------------------------------------------------------
# In-memory token blacklist
#
# Production upgrade path: replace with Redis SET + TTL
# ---------------------------------------------------------------------------

_blacklisted_jtis: set[str] = set()
_blacklist_lock = threading.Lock()


def blacklist_token(jti: str) -> None:
    """
    Add *jti* to the in-memory revocation set.

    Thread-safe; safe to call from any request handler.

    Production upgrade path: replace with Redis SET + TTL
        redis_client.setex(f"blacklist:{jti}", ttl_seconds, "1")
    """
    with _blacklist_lock:
        _blacklisted_jtis.add(jti)


def is_token_blacklisted(jti: str) -> bool:
    """
    Return True if *jti* has been revoked.

    Thread-safe; safe to call from any request handler.

    Production upgrade path: replace with Redis SET + TTL
        return redis_client.exists(f"blacklist:{jti}") > 0
    """
    with _blacklist_lock:
        return jti in _blacklisted_jtis


# ---------------------------------------------------------------------------
# Core auth dependency
# ---------------------------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency — decode the Bearer JWT and return the active User.

    Steps:
    1. Decode and validate the JWT signature / expiry via ``decode_access_token``.
    2. Check the ``jti`` claim against the in-memory blacklist (logout support).
    3. Look up the user by ``sub`` (user id) in the database.
    4. Verify the user account is active.

    Raises:
        HTTPException(401): Token invalid, expired, blacklisted, user not found,
                            or user account inactive.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Step 1 — decode JWT (raises 401 on invalid/expired token)
    payload = decode_access_token(token)

    # Step 2 — check blacklist
    jti: str | None = payload.get("jti")
    if not jti:
        raise credentials_exception
    if is_token_blacklisted(jti):
        raise credentials_exception

    # Step 3 — look up user
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise credentials_exception

    user: User | None = db.get(User, user_id)
    if user is None:
        raise credentials_exception

    # Step 4 — verify account is active
    if not user.is_active:
        raise credentials_exception

    return user


# ---------------------------------------------------------------------------
# Role-based access control factory
# ---------------------------------------------------------------------------

def require_role(*roles: UserRole) -> Callable[..., User]:
    """
    Dependency factory — return a FastAPI dependency that enforces role access.

    Usage::

        @router.get("/admin-only")
        def admin_endpoint(
            current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN))
        ):
            ...

    Args:
        *roles: One or more ``UserRole`` values that are permitted to access
                the endpoint.

    Returns:
        A FastAPI dependency function that calls ``get_current_user`` and then
        checks whether the authenticated user's role is in *roles*.

    Raises:
        HTTPException(403): Authenticated user's role is not in *roles*.
    """
    allowed = set(roles)

    def _check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return _check_role
