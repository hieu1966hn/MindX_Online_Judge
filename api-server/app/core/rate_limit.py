"""
In-memory login rate limiter using defaultdict + threading.Lock.

Production upgrade path: replace with Redis INCR + EXPIRE for distributed,
persistent rate limiting across multiple API server instances.
Example Redis approach:
    key = f"login_attempts:{ip}"
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, LOGIN_RATE_LIMIT_WINDOW_SECONDS)
    if count > LOGIN_RATE_LIMIT_ATTEMPTS:
        raise HTTPException(429)
"""

import time
import threading
from collections import defaultdict

from fastapi import HTTPException

from app.core.config import settings


# Maps IP address → list of attempt timestamps (float, from time.time())
_login_attempts: dict[str, list[float]] = defaultdict(list)

# Lock to protect concurrent reads/writes to _login_attempts
_lock = threading.Lock()


def check_login_rate_limit(ip: str) -> None:
    """
    Check whether the given IP has exceeded the login rate limit.

    Filters attempts within the last LOGIN_RATE_LIMIT_WINDOW_SECONDS seconds
    and raises HTTP 429 if the count is >= LOGIN_RATE_LIMIT_ATTEMPTS.

    Args:
        ip: The client IP address string.

    Raises:
        HTTPException(429): If the rate limit has been exceeded.
    """
    now = time.time()
    window = settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS

    with _lock:
        # Prune stale timestamps outside the current window
        recent = [t for t in _login_attempts[ip] if now - t < window]
        _login_attempts[ip] = recent

        if len(recent) >= settings.LOGIN_RATE_LIMIT_ATTEMPTS:
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Please try again later.",
            )


def record_login_attempt(ip: str) -> None:
    """
    Record a failed login attempt for the given IP.

    Appends the current timestamp to the IP's attempt list.

    Args:
        ip: The client IP address string.
    """
    with _lock:
        _login_attempts[ip].append(time.time())


def reset_login_attempts(ip: str) -> None:
    """
    Clear all recorded login attempts for the given IP.

    Should be called after a successful login to reset the counter.

    Args:
        ip: The client IP address string.
    """
    with _lock:
        _login_attempts[ip] = []
