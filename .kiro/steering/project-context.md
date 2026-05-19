---
inclusion: always
---

# MindX Online Judge — Project Context & Current State

> **Dành cho AI Agent:** Đây là file context chính. Đọc toàn bộ trước khi thực hiện bất kỳ task nào.

---

## 1. Tổng quan dự án

**Tên:** MindX Online Judge (Local-First MVP)
**Mục tiêu:** Nền tảng judge lập trình nội bộ cho MindX — giáo viên tạo bài, upload testcase; học sinh nộp bài, nhận kết quả tự động.
**Triết lý:** Local-first — chạy ngay với `pip install` + `python -m app.db.init_db` + `uvicorn`. Không cần Docker, PostgreSQL, Redis.

**Tài liệu tham khảo đầy đủ:**
- `README.md` — Vision, user flows, MVP scope, phases
- `docs/architecture.md` — Sơ đồ kiến trúc, communication flows, setup commands
- `docs/decision-log.md` — 6 ADRs giải thích các quyết định kỹ thuật
- `.kiro/specs/mindx-online-judge/requirements.md` — 10 requirements chi tiết với acceptance criteria
- `.kiro/specs/mindx-online-judge/design.md` — Technical design
- `.kiro/specs/mindx-online-judge/tasks.md` — Task list với dependency graph (SOURCE OF TRUTH cho tiến độ)

---

## 2. Tech Stack

| Layer | Technology | Ghi chú |
|-------|-----------|---------|
| Backend | FastAPI 0.111 + Python 3.12 + SQLAlchemy 2.0 + SQLite + Alembic | Không dùng PostgreSQL trong MVP |
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind CSS v3 | `output: 'standalone'` |
| Code Editor | Monaco Editor (`@monaco-editor/react`) | |
| Auth | JWT HS256 (`python-jose`) + bcrypt (`passlib`) | httpOnly cookie |
| Rate Limit | In-memory `defaultdict` + `threading.Lock` | Upgrade path: Redis |
| Token Blacklist | In-memory `set[str]` | Upgrade path: Redis SET+TTL |
| Judge | `LocalSubprocessJudgeRunner` (subprocess trực tiếp) | **Không có sandbox** — chỉ cho local dev |
| Tests | pytest + Hypothesis (backend), Vitest + RTL (frontend) | |

---

## 3. Cấu trúc monorepo

```
MindX_Online_Judge/
├── api-server/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py             ✅ FastAPI app, CORS, routers, /health
│   │   ├── core/
│   │   │   ├── config.py       ✅ pydantic-settings
│   │   │   ├── security.py     ✅ bcrypt + JWT HS256 + jti
│   │   │   ├── deps.py         ✅ get_current_user, require_role, blacklist
│   │   │   └── rate_limit.py   ✅ in-memory rate limiter
│   │   ├── db/
│   │   │   ├── base.py         ✅ declarative_base()
│   │   │   ├── session.py      ✅ SQLite engine, get_db()
│   │   │   └── migrations/     ✅ Alembic + 001_create_initial_tables
│   │   ├── models/
│   │   │   ├── user.py         ✅ User + UserRole enum (SQLAlchemy 2.0)
│   │   │   ├── password_reset_token.py  ✅ PasswordResetToken ORM
│   │   │   ├── problem.py      ❌ TODO stub
│   │   │   └── submission.py   ❌ TODO stub
│   │   ├── schemas/
│   │   │   ├── user.py         ✅ UserBase, UserCreate, UserRead, UserUpdate
│   │   │   ├── auth.py         ✅ LoginRequest, TokenResponse, TokenPayload
│   │   │   ├── problem.py      ❌ TODO stub
│   │   │   └── submission.py   ❌ TODO stub
│   │   ├── services/
│   │   │   ├── auth_service.py ✅ authenticate, create_user, password_reset (6 functions)
│   │   │   ├── problem_service.py   ❌ TODO stub
│   │   │   └── submission_service.py ❌ TODO stub
│   │   ├── routers/
│   │   │   ├── auth.py         ❌ Stub rỗng (chỉ có APIRouter())
│   │   │   ├── users.py        ❌ Stub rỗng
│   │   │   ├── problems.py     ❌ Stub rỗng
│   │   │   └── submissions.py  ❌ Stub rỗng
│   │   └── judge/
│   │       ├── base.py         ⚠️ AbstractJudgeRunner skeleton (chưa implement)
│   │       └── local_runner.py ⚠️ LocalSubprocessJudgeRunner skeleton (chưa implement)
│   ├── requirements.txt        ✅ Đầy đủ (bcrypt==4.0.1 pinned)
│   └── requirements-dev.txt    ✅ pytest + hypothesis + httpx
│
├── web-app/                    # Next.js frontend
│   ├── package.json            ✅ Tất cả deps pinned (no ^ or ~)
│   ├── tsconfig.json           ✅ strict, @/* alias
│   ├── tailwind.config.ts      ✅ verdict colors, font families
│   ├── next.config.ts          ✅ standalone + API rewrites
│   ├── postcss.config.js       ✅
│   └── src/
│       ├── middleware.ts        ✅ Edge Runtime RBAC (jose.decodeJwt)
│       ├── types/
│       │   ├── auth.ts         ✅ UserRole, User, TokenPayload, LoginRequest, LoginResponse
│       │   ├── problem.ts      ✅ Problem, ProblemCreate, Language
│       │   ├── submission.ts   ✅ Verdict enum, Submission, SubmissionCreate, TestcaseResult
│       │   └── index.ts        ✅ barrel export
│       ├── lib/
│       │   ├── api.ts          ✅ 12 API functions (fetch-based, cookie auth)
│       │   └── auth.ts         ✅ decodeToken, isTokenExpired, hasRequiredRole, getTokenFromCookie
│       ├── app/                ❌ Hoàn toàn rỗng (chưa có page nào)
│       └── components/         ❌ Hoàn toàn rỗng
│
├── problem-packages/
│   └── sum_two_numbers/        ✅ Seed problem (problem.yaml, statement.md, tests/)
├── storage/submissions/        ✅ Thư mục lưu source code
├── .env.example                ✅ Đầy đủ vars
└── .kiro/specs/mindx-online-judge/
    ├── requirements.md         ✅
    ├── design.md               ✅
    └── tasks.md                ✅ SOURCE OF TRUTH — đọc để biết task nào cần làm tiếp
```

---

## 4. Trạng thái tiến độ hiện tại

**Tổng tiến độ: ~45% MVP**

### ✅ Round 1 — Repository Setup & Backend Scaffolding (HOÀN THÀNH)
Wave 0–1: Cấu trúc thư mục, config, DB session, main.py

### ✅ Round 2 — User Model + Auth Core (HOÀN THÀNH)
Wave 2–4:
- User ORM model + PasswordResetToken ORM
- Pydantic schemas (user, auth)
- Alembic migrations (4 bảng: users, problems, submissions, password_reset_tokens)
- security.py (bcrypt + JWT)
- rate_limit.py (in-memory)
- deps.py (get_current_user, require_role, blacklist)
- auth_service.py (6 functions)
- Frontend: package.json, tsconfig, tailwind, next.config, types/, lib/api.ts, lib/auth.ts, middleware.ts

### 🔴 Round 3 — Auth Routers + Problem Model + Auth UI (CHƯA BẮT ĐẦU)
Wave 5–6 (tasks sẵn sàng):
- **5.1** `routers/auth.py` — login, logout, password-reset endpoints
- **5.2** `routers/users.py` — CRUD users endpoints
- **6.1** `models/problem.py` — Problem ORM model
- **6.2** `schemas/problem.py` — ProblemCreate, ProblemRead, ProblemUpdate, ProblemYaml
- **12.2** `components/auth/LoginForm.tsx`
- **12.3** Next.js API routes (auth/login, auth/logout)
- **12.4** `components/auth/AuthGuard.tsx`

### 🔴 Round 4 — Problem Service + Judge + Submission (CHƯA BẮT ĐẦU)
Wave 7–8: problem_service, problems router, judge runner, submission model/service/router

### 🔴 Round 5 — Seeds + Init Script + Backend Checkpoint (CHƯA BẮT ĐẦU)
Wave 9–12: seeds.py, init_db.py, README update, Checkpoint Task 10

### 🔴 Round 6–8 — Frontend Pages + Tests (CHƯA BẮT ĐẦU)
Wave 5–13 (FE): Auth pages, Dashboard, Problem pages, Submission pages, Tests

---

## 5. Conventions & Coding Patterns

### Backend (Python)
- **SQLAlchemy 2.0 style**: dùng `Mapped[T]` và `mapped_column()`, KHÔNG dùng `Column()` cũ
- **UUID**: `str(uuid.uuid4())` — lưu dưới dạng `String(36)`, KHÔNG dùng native UUID type (SQLite không hỗ trợ)
- **Datetime**: `datetime.now(timezone.utc)` — KHÔNG dùng `datetime.utcnow()` (deprecated)
- **Pydantic V2**: dùng `model_config = ConfigDict(from_attributes=True)` cho ORM models
- **Imports**: absolute imports (`from app.core.config import settings`)
- **Error handling**: raise `HTTPException` với status code cụ thể
- **Security**: KHÔNG log token/password, dùng generic error messages cho auth failures
- **bcrypt pin**: `bcrypt==4.0.1` (passlib 1.7.4 không tương thích bcrypt >= 4.1)

### Frontend (TypeScript)
- **Path alias**: `@/*` → `./src/*`
- **Types**: import từ `@/types` (barrel export)
- **API calls**: dùng `lib/api.ts`, KHÔNG fetch trực tiếp trong components
- **Auth**: token trong httpOnly cookie `access_token`, đọc qua `lib/auth.ts`
- **Tailwind**: dùng verdict colors đã định nghĩa (`verdict-ac`, `verdict-wa`, etc.)
- **No open ranges**: tất cả npm deps phải pinned exact version

### Task Execution
- Đọc `tasks.md` để biết task nào ready (không có dependency chưa xong)
- Mỗi task có `_Requirements: X` — đọc `requirements.md` để hiểu acceptance criteria
- Tasks đánh `*` là optional — có thể skip để đạt MVP nhanh hơn
- Sau khi implement, verify bằng cách chạy import Python hoặc tsc --noEmit

---

## 6. Seed Accounts (sau khi chạy init_db)

| Email | Password | Role |
|-------|----------|------|
| superadmin@mindx.edu.vn | SuperAdmin@123 | super_admin |
| admin@mindx.edu.vn | Admin@123 | admin |
| teacher@mindx.edu.vn | Teacher@123 | teacher |
| student@mindx.edu.vn | Student@123 | student |

---

## 7. Lệnh chạy local

```bash
# Backend
cd api-server
pip install -r requirements-dev.txt
python -m app.db.init_db
uvicorn app.main:app --reload --port 8000

# Frontend
cd web-app
npm install
npm run dev

# Tests
cd api-server && pytest tests/ -v
cd web-app && npx vitest --run
```

**URLs:** Frontend: http://localhost:3000 | API: http://localhost:8000 | Docs: http://localhost:8000/docs

---

## 8. Production Hardening (KHÔNG thuộc MVP)

Các upgrade path đã được document trong `docs/decision-log.md`:
- SQLite → PostgreSQL
- In-memory rate limit → Redis INCR+EXPIRE
- In-memory blacklist → Redis SET+TTL
- LocalSubprocessJudgeRunner → DockerSandboxJudgeRunner
- Sync judging → Redis job queue + worker process

**KHÔNG implement các thứ này trong MVP.**

---

## 9. Quy tắc cho AI Agent

1. **Đọc `tasks.md` trước** — đây là source of truth cho task nào cần làm tiếp theo
2. **Không tự ý thêm dependencies** mới ngoài những gì đã có trong requirements.txt / package.json
3. **Không implement Production Hardening** (PostgreSQL, Redis, Docker) trong MVP
4. **Verify sau khi implement** — chạy `python -c "import app.xxx"` hoặc `tsc --noEmit`
5. **Giữ stub files** — nếu một file chỉ có `# TODO`, thay thế hoàn toàn bằng implementation thực
6. **Không break existing code** — kiểm tra imports trước khi thay đổi interface
7. **Comment upgrade path** — mọi in-memory structure phải có comment Redis upgrade path
8. **Generic auth errors** — login/password-reset KHÔNG được tiết lộ email có tồn tại hay không
