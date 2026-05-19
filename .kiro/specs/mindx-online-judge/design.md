# Design Document — MindX Online Judge (Local-First MVP)

## Overview

Tài liệu này mô tả thiết kế kỹ thuật cho **Local-First MVP** của MindX Online Judge.

**Nguyên tắc cốt lõi:** MVP phải chạy được ngay trên máy local với một lệnh duy nhất — không cần Docker, không cần PostgreSQL, không cần Redis. Mọi thứ đều dùng SQLite và local filesystem.

**Phạm vi MVP:**
1. Problem package structure (chuẩn thư mục + `problem.yaml`)
2. Upload/import problem statement (`.md`, `.txt`, `.docx`, `.pdf`)
3. Upload testcase pairs (ZIP hoặc từng cặp `.in`/`.out`)
4. Student code editor (Monaco hoặc textarea) + file upload
5. Submit code → LocalSubprocessJudgeRunner → AC/WA/TLE/RE/CE
6. Submission history và kết quả chi tiết
7. Teacher/Admin dashboard cơ bản

**Upgrade path (Production Hardening — không thuộc MVP):**
- SQLite → PostgreSQL
- In-memory rate limiting → Redis
- LocalSubprocessJudgeRunner → DockerSandboxJudgeRunner
- Synchronous judging → Async Redis job queue
- Docker Compose cho full production stack

---

## Architecture

### MVP Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      Browser                            │
│              (Next.js SSR/CSR)                          │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (localhost:3000 → localhost:8000)
┌──────────────────────▼──────────────────────────────────┐
│                   api-server                            │
│              FastAPI + Python 3.12                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              SQLite Database                    │   │
│  │         (api-server/data/mindx.db)              │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │         LocalSubprocessJudgeRunner              │   │
│  │   (runs in background thread, same process)     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │           Local Filesystem Storage              │   │
│  │  problem-packages/  submissions/  storage/      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Production Hardening Architecture (Future)

```
Browser → Next.js → FastAPI → PostgreSQL
                           → Redis (rate limit, token blacklist, job queue)
                           → DockerSandboxJudgeRunner (judge-worker process)
                           → Local/S3 Filesystem
```

### Monorepo Structure

```
mindx-online-judge/
├── web-app/                    # Next.js frontend
│   ├── src/
│   │   ├── app/                # App Router pages
│   │   │   ├── (auth)/         # login, forgot-password, reset-password
│   │   │   ├── (protected)/    # dashboard, problems, submissions
│   │   │   └── api/            # Next.js API routes (BFF)
│   │   ├── components/
│   │   │   ├── auth/           # LoginForm, AuthGuard
│   │   │   ├── editor/         # CodeEditor (Monaco wrapper)
│   │   │   └── layout/         # Navbar, DashboardLayout
│   │   ├── lib/
│   │   │   ├── api.ts          # HTTP client
│   │   │   └── auth.ts         # JWT decode, role helpers
│   │   └── types/              # TypeScript types
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.ts          # output: 'standalone' (for future Docker)
│
├── api-server/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── core/
│   │   │   ├── config.py       # Settings (pydantic-settings)
│   │   │   ├── security.py     # bcrypt + JWT
│   │   │   ├── deps.py         # Auth dependencies
│   │   │   └── rate_limit.py   # In-memory rate limiter (MVP)
│   │   ├── models/
│   │   │   ├── user.py         # User ORM model
│   │   │   ├── problem.py      # Problem ORM model
│   │   │   └── submission.py   # Submission ORM model
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── problem.py
│   │   │   └── submission.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── problems.py
│   │   │   └── submissions.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── problem_service.py
│   │   │   └── submission_service.py
│   │   ├── judge/
│   │   │   ├── base.py         # AbstractJudgeRunner interface
│   │   │   └── local_runner.py # LocalSubprocessJudgeRunner
│   │   └── db/
│   │       ├── base.py         # SQLAlchemy Base
│   │       ├── session.py      # SQLite engine + get_db()
│   │       ├── migrations/     # Alembic migrations
│   │       ├── seeds.py        # Seed data
│   │       └── init_db.py      # Setup script
│   ├── data/                   # SQLite database file (gitignored)
│   ├── tests/
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── problem-packages/           # Problem workspace (local filesystem)
│   └── sum_two_numbers/
│       ├── problem.yaml
│       ├── statement.md
│       └── tests/
│           ├── samples/
│           │   ├── 01.in
│           │   └── 01.out
│           └── hidden/
│               ├── 01.in
│               └── 01.out
│
├── storage/                    # Uploaded files (gitignored)
│   └── submissions/            # Submitted source code snapshots
│
├── docs/
│   ├── architecture.md
│   └── decision-log.md
│
├── infra/                      # Production Hardening (future)
│   ├── docker-compose.yml
│   └── docker-compose.db.yml
│
├── .env.example
└── README.md
```

---

## Components and Interfaces

### Backend Components

#### 1. Auth Router (`/api/v1/auth`)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/login` | Xác thực, trả về JWT | No |
| POST | `/logout` | Vô hiệu hóa token (in-memory blacklist) | Yes |
| POST | `/password-reset/request` | Tạo reset token, log ra console | No |
| POST | `/password-reset/confirm` | Xác nhận token, đặt mật khẩu mới | No |

#### 2. Users Router (`/api/v1/users`)

| Method | Path | Description | Min Role |
|--------|------|-------------|----------|
| GET | `/me` | Thông tin user hiện tại | Student |
| GET | `/` | Danh sách users | Admin |
| POST | `/` | Tạo user mới | Admin |
| PATCH | `/{user_id}` | Cập nhật user | Admin |

#### 3. Problems Router (`/api/v1/problems`)

| Method | Path | Description | Min Role |
|--------|------|-------------|----------|
| GET | `/` | Danh sách problems | Student |
| POST | `/` | Tạo problem mới | Teacher |
| GET | `/{problem_id}` | Chi tiết problem | Student |
| PATCH | `/{problem_id}` | Cập nhật problem | Teacher |
| DELETE | `/{problem_id}` | Xóa/archive problem | Teacher |
| POST | `/{problem_id}/statement` | Upload statement file | Teacher |
| POST | `/{problem_id}/testcases` | Upload testcase ZIP | Teacher |
| POST | `/{problem_id}/testcases/pair` | Upload cặp .in/.out | Teacher |

#### 4. Submissions Router (`/api/v1/submissions`)

| Method | Path | Description | Min Role |
|--------|------|-------------|----------|
| POST | `/` | Nộp bài | Student |
| GET | `/` | Lịch sử submission của user | Student |
| GET | `/{submission_id}` | Chi tiết submission | Student |
| GET | `/admin/all` | Tất cả submissions | Admin |

#### 5. LocalSubprocessJudgeRunner

```python
# api-server/app/judge/base.py
from abc import ABC, abstractmethod
from app.models.submission import Submission

class AbstractJudgeRunner(ABC):
    @abstractmethod
    def judge(self, submission: Submission) -> None:
        """Judge a submission and update its verdict in the database."""
        ...

# api-server/app/judge/local_runner.py
import subprocess
import tempfile
import shutil
from pathlib import Path
from app.judge.base import AbstractJudgeRunner

class LocalSubprocessJudgeRunner(AbstractJudgeRunner):
    """
    MVP judge runner — runs code directly on the host using subprocess.
    No sandbox isolation. Suitable for trusted local development only.
    
    Upgrade path: Replace with DockerSandboxJudgeRunner for production.
    """
    
    def judge(self, submission: Submission) -> None:
        workdir = Path(tempfile.mkdtemp())
        try:
            self._run_judge(submission, workdir)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
    
    def _compile(self, source: str, language: str, workdir: Path) -> tuple[bool, str]:
        """Returns (success, error_output)."""
        ...
    
    def _run_testcase(self, binary: Path, input_path: Path, expected_path: Path,
                      time_limit_ms: int) -> str:
        """Returns verdict: AC, WA, TLE, RE."""
        ...
```

#### 6. In-Memory Rate Limiter (MVP)

```python
# api-server/app/core/rate_limit.py
import time
from collections import defaultdict
from threading import Lock

# MVP: in-memory sliding window
# Upgrade path: replace with Redis INCR + EXPIRE for production
_login_attempts: dict[str, list[float]] = defaultdict(list)
_lock = Lock()

def check_login_rate_limit(ip: str) -> None:
    """Raise HTTPException(429) if IP has exceeded 10 attempts in 15 minutes."""
    ...

def record_login_attempt(ip: str) -> None:
    ...

def reset_login_attempts(ip: str) -> None:
    ...
```

#### 7. Token Blacklist (MVP)

```python
# MVP: in-memory set (lost on restart — acceptable for local dev)
# Upgrade path: replace with Redis SET + TTL for production
_blacklisted_jtis: set[str] = set()

def blacklist_token(jti: str) -> None:
    _blacklisted_jtis.add(jti)

def is_token_blacklisted(jti: str) -> bool:
    return jti in _blacklisted_jtis
```

### Frontend Components

#### Page Structure

```
src/app/
├── (auth)/
│   ├── login/page.tsx
│   ├── forgot-password/page.tsx
│   └── reset-password/page.tsx
├── (protected)/
│   ├── layout.tsx              # Auth guard
│   ├── dashboard/page.tsx      # Role-aware redirect
│   ├── student/
│   │   ├── dashboard/page.tsx
│   │   └── problems/
│   │       ├── page.tsx        # Problem list
│   │       └── [id]/
│   │           ├── page.tsx    # Problem detail + editor
│   │           └── submissions/page.tsx
│   ├── teacher/
│   │   ├── dashboard/page.tsx
│   │   └── problems/
│   │       ├── page.tsx
│   │       ├── new/page.tsx    # Create problem
│   │       └── [id]/
│   │           ├── edit/page.tsx
│   │           └── testcases/page.tsx
│   └── admin/
│       ├── dashboard/page.tsx
│       ├── users/page.tsx
│       └── submissions/page.tsx
└── 403/page.tsx
```

#### Key Components

| Component | Path | Description |
|-----------|------|-------------|
| `LoginForm` | `components/auth/LoginForm.tsx` | Form đăng nhập |
| `AuthGuard` | `components/auth/AuthGuard.tsx` | Client-side token check |
| `CodeEditor` | `components/editor/CodeEditor.tsx` | Monaco Editor wrapper |
| `SubmitButton` | `components/editor/SubmitButton.tsx` | Submit + hiển thị verdict |
| `VerdictBadge` | `components/submission/VerdictBadge.tsx` | AC/WA/TLE/RE/CE badge |
| `Navbar` | `components/layout/Navbar.tsx` | Navigation bar |
| `DashboardLayout` | `components/layout/DashboardLayout.tsx` | Layout wrapper |

---

## Data Models

### SQLite Schema (MVP)

```sql
-- Users
CREATE TABLE users (
    id           TEXT PRIMARY KEY,  -- UUID as string
    name         TEXT NOT NULL,
    email        TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role         TEXT NOT NULL DEFAULT 'student'
                 CHECK(role IN ('student','teacher','admin','super_admin')),
    is_active    INTEGER NOT NULL DEFAULT 1,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);
CREATE INDEX idx_users_email ON users(email);

-- Problems
CREATE TABLE problems (
    id              TEXT PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    title           TEXT NOT NULL,
    statement_md    TEXT NOT NULL DEFAULT '',
    time_limit_ms   INTEGER NOT NULL DEFAULT 1000,
    memory_limit_mb INTEGER NOT NULL DEFAULT 256,
    allowed_languages TEXT NOT NULL DEFAULT '["python3","cpp17"]',  -- JSON array
    scoring_mode    TEXT NOT NULL DEFAULT 'all_or_nothing'
                    CHECK(scoring_mode IN ('all_or_nothing','partial_score')),
    is_visible      INTEGER NOT NULL DEFAULT 0,
    is_archived     INTEGER NOT NULL DEFAULT 0,
    package_path    TEXT,           -- path to problem-packages/{code}/
    created_by      TEXT NOT NULL REFERENCES users(id),
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- Submissions
CREATE TABLE submissions (
    id           TEXT PRIMARY KEY,
    problem_id   TEXT NOT NULL REFERENCES problems(id),
    user_id      TEXT NOT NULL REFERENCES users(id),
    language     TEXT NOT NULL,
    source_path  TEXT NOT NULL,     -- path to storage/submissions/{id}/main.py|cpp
    verdict      TEXT NOT NULL DEFAULT 'PD'
                 CHECK(verdict IN ('PD','AC','WA','TLE','RE','CE')),
    score        INTEGER NOT NULL DEFAULT 0,
    compile_error TEXT,
    testcase_results TEXT,          -- JSON array of per-testcase results
    judged_at    TEXT,
    created_at   TEXT NOT NULL
);
CREATE INDEX idx_submissions_user ON submissions(user_id);
CREATE INDEX idx_submissions_problem ON submissions(problem_id);

-- Password Reset Tokens (MVP: stored in SQLite instead of Redis)
CREATE TABLE password_reset_tokens (
    token        TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL REFERENCES users(id),
    expires_at   TEXT NOT NULL,
    used         INTEGER NOT NULL DEFAULT 0
);
```

### SQLAlchemy ORM Models

```python
# app/models/user.py
import enum, uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum
from app.db.base import Base

class UserRole(str, enum.Enum):
    STUDENT    = "student"
    TEACHER    = "teacher"
    ADMIN      = "admin"
    SUPER_ADMIN = "super_admin"

class User(Base):
    __tablename__ = "users"
    id            = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name          = Column(String(200), nullable=False)
    email         = Column(String(254), nullable=False, unique=True, index=True)
    password_hash = Column(String(128), nullable=False)
    role          = Column(SAEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    is_active     = Column(Boolean, nullable=False, default=True)
    created_at    = Column(DateTime(timezone=True), nullable=False,
                           default=lambda: datetime.now(timezone.utc))
    updated_at    = Column(DateTime(timezone=True), nullable=False,
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
```

```python
# app/models/problem.py
import uuid, json
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from app.db.base import Base

class Problem(Base):
    __tablename__ = "problems"
    id              = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code            = Column(String(50), nullable=False, unique=True)
    title           = Column(String(200), nullable=False)
    statement_md    = Column(Text, nullable=False, default="")
    time_limit_ms   = Column(Integer, nullable=False, default=1000)
    memory_limit_mb = Column(Integer, nullable=False, default=256)
    allowed_languages = Column(String(200), nullable=False, default='["python3","cpp17"]')
    scoring_mode    = Column(String(20), nullable=False, default="all_or_nothing")
    is_visible      = Column(Boolean, nullable=False, default=False)
    is_archived     = Column(Boolean, nullable=False, default=False)
    package_path    = Column(String(500), nullable=True)
    created_by      = Column(String(36), nullable=False)
    created_at      = Column(DateTime(timezone=True), nullable=False)
    updated_at      = Column(DateTime(timezone=True), nullable=False)
```

```python
# app/models/submission.py
import uuid
from sqlalchemy import Column, String, Integer, DateTime, Text
from app.db.base import Base

class Submission(Base):
    __tablename__ = "submissions"
    id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    problem_id       = Column(String(36), nullable=False)
    user_id          = Column(String(36), nullable=False)
    language         = Column(String(20), nullable=False)
    source_path      = Column(String(500), nullable=False)
    verdict          = Column(String(5), nullable=False, default="PD")
    score            = Column(Integer, nullable=False, default=0)
    compile_error    = Column(Text, nullable=True)
    testcase_results = Column(Text, nullable=True)  # JSON
    judged_at        = Column(DateTime(timezone=True), nullable=True)
    created_at       = Column(DateTime(timezone=True), nullable=False)
```

### Pydantic Schemas

```python
# app/schemas/auth.py
from pydantic import BaseModel
from app.models.user import UserRole

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400

class TokenPayload(BaseModel):
    sub: str        # user id
    role: UserRole
    exp: int
    iat: int
    jti: str
```

```python
# app/schemas/problem.py
from pydantic import BaseModel
from typing import Literal

class ProblemCreate(BaseModel):
    code: str
    title: str
    time_limit_ms: int = 1000
    memory_limit_mb: int = 256
    allowed_languages: list[str] = ["python3", "cpp17"]
    scoring_mode: Literal["all_or_nothing", "partial_score"] = "all_or_nothing"

class ProblemRead(ProblemCreate):
    id: str
    statement_md: str
    is_visible: bool
    is_archived: bool
    created_at: str
    model_config = {"from_attributes": True}
```

```python
# app/schemas/submission.py
from pydantic import BaseModel

class SubmissionCreate(BaseModel):
    problem_id: str
    language: str
    source_code: str  # raw code string OR loaded from uploaded file

class TestcaseResult(BaseModel):
    index: int
    verdict: str
    runtime_ms: int | None = None
    is_hidden: bool = False

class SubmissionRead(BaseModel):
    id: str
    problem_id: str
    language: str
    verdict: str
    score: int
    compile_error: str | None
    testcase_results: list[TestcaseResult] | None
    judged_at: str | None
    created_at: str
    model_config = {"from_attributes": True}
```

### Problem Package Format

```yaml
# problem-packages/{code}/problem.yaml
code: sum_two_numbers
title: "Tổng hai số"
time_limit_ms: 1000
memory_limit_mb: 256
allowed_languages:
  - python3
  - cpp17
  - cpp20
scoring_mode: all_or_nothing
```

```
problem-packages/sum_two_numbers/
├── problem.yaml
├── statement.md
└── tests/
    ├── samples/
    │   ├── 01.in
    │   └── 01.out
    └── hidden/
        ├── 01.in
        ├── 01.out
        ├── 02.in
        └── 02.out
```

---

## Correctness Properties

### Property 1: Password hash round-trip

*For any* valid plaintext password string, hashing it and then verifying the original plaintext against the hash SHALL return `True`; verifying any different string against the same hash SHALL return `False`.

**Validates: Requirement 1.1**

---

### Property 2: JWT token round-trip

*For any* valid User with a given `id` and `role`, creating an access token and then decoding it SHALL produce a payload whose `sub` equals the User's `id` and whose `role` equals the User's role.

**Validates: Requirements 1.1, 2.1**

---

### Property 3: Role-based access enforcement

*For any* HTTP request to a protected route with a valid JWT, the response status code SHALL be 403 if and only if the token's role is not in the set of roles permitted for that route.

**Validates: Requirements 2.2, 2.3, 2.4**

---

### Property 4: Unauthenticated request rejection

*For any* protected route, a request made without a valid JWT SHALL always receive an HTTP 401 response.

**Validates: Requirement 2.6**

---

### Property 5: Problem package round-trip

*For any* valid `problem.yaml`, parsing it into a Problem object then serializing it back to YAML then parsing again SHALL produce a Problem object with field values equal to those of the original.

**Validates: Requirement 3.4**

---

### Property 6: Testcase verdict consistency

*For any* Submission where all testcases pass (AC), the final verdict SHALL be AC; *for any* Submission where at least one testcase has verdict TLE, the final verdict SHALL be TLE regardless of other testcase verdicts.

**Validates: Requirement 6.9**

---

### Property 7: Admin cannot assign Super_Admin role

*For any* Admin user attempting to create or update a User with role `super_admin`, the System SHALL return HTTP 403.

**Validates: Requirement 2.5**

---

## Error Handling

### HTTP Error Response Format

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Email hoặc mật khẩu không đúng.",
    "details": null
  }
}
```

### Error Code Catalog

| HTTP Status | Error Code | Tình huống |
|-------------|------------|------------|
| 400 | `VALIDATION_ERROR` | Request body không hợp lệ |
| 401 | `UNAUTHENTICATED` | Không có token hoặc token không hợp lệ |
| 401 | `TOKEN_EXPIRED` | JWT đã hết hạn |
| 403 | `FORBIDDEN` | Role không đủ quyền |
| 403 | `ROLE_ESCALATION_DENIED` | Admin cố gán role Super_Admin |
| 404 | `NOT_FOUND` | Resource không tồn tại |
| 409 | `EMAIL_ALREADY_EXISTS` | Email đã được đăng ký |
| 422 | `INVALID_RESET_TOKEN` | Token reset không hợp lệ hoặc đã hết hạn |
| 429 | `LOGIN_RATE_LIMITED` | Quá nhiều lần đăng nhập thất bại |
| 500 | `INTERNAL_ERROR` | Lỗi server không xác định |

---

## Testing Strategy

### Backend Testing (pytest + Hypothesis)

```python
# tests/test_security_properties.py
from hypothesis import given, settings
from hypothesis import strategies as st
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

@given(password=st.text(min_size=1, max_size=72))
@settings(max_examples=100)
def test_password_hash_roundtrip(password):
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True

@given(
    user_id=st.uuids(),
    role=st.sampled_from(["student", "teacher", "admin", "super_admin"])
)
@settings(max_examples=100)
def test_jwt_roundtrip(user_id, role):
    token = create_access_token({"sub": str(user_id), "role": role})
    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["role"] == role
```

### Frontend Testing (Vitest + React Testing Library)

```typescript
// LoginForm.test.tsx
test('shows validation error for empty email', async () => {
  render(<LoginForm />)
  fireEvent.click(screen.getByRole('button', { name: /đăng nhập/i }))
  expect(await screen.findByText(/email không được để trống/i)).toBeInTheDocument()
})
```

### Test Coverage Targets

| Layer | Target |
|-------|--------|
| `app/core/security.py` | 100% |
| `app/judge/local_runner.py` | ≥ 90% |
| `app/routers/auth.py` | ≥ 90% |
| `app/routers/submissions.py` | ≥ 85% |
| Frontend auth components | ≥ 80% |

---

## Local Development Setup

```bash
# 1. Clone repo và cài dependencies
cd api-server
pip install -r requirements-dev.txt

# 2. Khởi tạo DB và seed data
python -m app.db.init_db

# 3. Chạy API server
uvicorn app.main:app --reload --port 8000

# 4. Chạy frontend (terminal khác)
cd web-app
npm install
npm run dev

# 5. Chạy tests
pytest api-server/tests/ -v
cd web-app && npx vitest --run
```

**Service URLs:**
- Frontend: http://localhost:3000
- API Server: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Seed accounts:**
| Email | Password | Role |
|-------|----------|------|
| superadmin@mindx.edu.vn | SuperAdmin@123 | Super_Admin |
| admin@mindx.edu.vn | Admin@123 | Admin |
| teacher@mindx.edu.vn | Teacher@123 | Teacher |
| student@mindx.edu.vn | Student@123 | Student |
