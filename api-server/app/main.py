"""
MindX Online Judge — FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.problems import router as problems_router
from app.routers.submissions import router as submissions_router

# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="MindX Online Judge",
    version="0.1.0",
    description="Local-first MVP",
)

# ---------------------------------------------------------------------------
# CORS middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.NEXT_PUBLIC_API_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(problems_router, prefix="/api/v1/problems", tags=["problems"])
app.include_router(submissions_router, prefix="/api/v1/submissions", tags=["submissions"])

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Return a simple liveness response."""
    return {"status": "ok", "version": "0.1.0"}
