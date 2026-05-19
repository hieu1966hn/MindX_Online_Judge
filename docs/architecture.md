# MindX Online Judge — Architecture Overview

## Introduction

MindX Online Judge là nền tảng judge lập trình nội bộ dành cho MindX. Giáo viên tạo và quản lý bài tập, upload testcase, học sinh nộp bài và nhận kết quả chấm tự động.

**Triết lý thiết kế:** Local-first MVP — chạy được ngay trên máy local với `pip install` + một lệnh setup, không cần Docker, PostgreSQL, hay Redis. Production Hardening là bước nâng cấp tùy chọn sau khi MVP đã hoạt động ổn định.

---

## MVP Architecture (Local-First)

```
┌─────────────────────────────────────────────────────────┐
│                      Browser                            │
│         Next.js (localhost:3000)                        │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP
┌──────────────────────▼──────────────────────────────────┐
│              FastAPI (localhost:8000)                   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  SQLite  (api-server/data/mindx.db)              │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  LocalSubprocessJudgeRunner                      │  │
│  │  (background thread, same process)               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Local Filesystem                                │  │
│  │  problem-packages/   storage/submissions/        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### MVP Components

| Component | Technology | Vai trò |
|-----------|-----------|---------|
| Frontend | Next.js 14 + TypeScript + Tailwind | UI, route protection, code editor |
| Backend | FastAPI + Python 3.12 | REST API, business logic, auth |
| Database | SQLite (via SQLAlchemy) | Lưu trữ users, problems, submissions |
| Judge | LocalSubprocessJudgeRunner | Chấm bài bằng subprocess trực tiếp |
| Storage | Local filesystem | Problem packages, submitted source code |
| Rate Limiting | In-memory (Python dict) | Login attempt tracking |
| Token Blacklist | In-memory (Python set) | Logout token invalidation |

---

## Production Hardening Architecture (Future Upgrade)

```
┌──────────────────────────────────────────────────────────────┐
│                         Browser                              │
│                   Next.js (SSR/CSR)                          │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────▼───────────────────────────────────┐
│                      FastAPI                                 │
│                                                              │
│  PostgreSQL (primary DB)    Redis (rate limit, blacklist,    │
│                              job queue, reset tokens)        │
└──────────────────────────────────────────────────────────────┘
                           │ Redis job queue
┌──────────────────────────▼───────────────────────────────────┐
│              DockerSandboxJudgeRunner (judge-worker)         │
│  Docker container per submission — no network, resource      │
│  limits: CPU time, wall time, memory, output size, process   │
└──────────────────────────────────────────────────────────────┘
```

---

## Monorepo Structure

```
mindx-online-judge/
├── web-app/                    # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/         # login, forgot-password, reset-password
│   │   │   ├── (protected)/    # dashboard, problems, submissions
│   │   │   └── api/            # Next.js API routes (BFF)
│   │   ├── components/
│   │   │   ├── auth/           # LoginForm, AuthGuard
│   │   │   ├── editor/         # CodeEditor (Monaco), SubmitButton
│   │   │   └── layout/         # Navbar, DashboardLayout
│   │   ├── lib/
│   │   │   ├── api.ts          # HTTP client
│   │   │   └── auth.ts         # JWT decode, role helpers
│   │   └── types/              # TypeScript types
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.ts
│
├── api-server/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py       # pydantic-settings
│   │   │   ├── security.py     # bcrypt + JWT
│   │   │   ├── deps.py         # auth dependencies + in-memory blacklist
│   │   │   └── rate_limit.py   # in-memory rate limiter
│   │   ├── models/             # SQLAlchemy ORM (SQLite)
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── routers/            # auth, users, problems, submissions
│   │   ├── services/           # business logic
│   │   ├── judge/
│   │   │   ├── base.py         # AbstractJudgeRunner
│   │   │   └── local_runner.py # LocalSubprocessJudgeRunner
│   │   └── db/
│   │       ├── base.py
│   │       ├── session.py      # SQLite engine
│   │       ├── migrations/     # Alembic
│   │       ├── seeds.py
│   │       └── init_db.py      # python -m app.db.init_db
│   ├── data/                   # SQLite DB file (gitignored)
│   ├── tests/
│   ├── requirements.txt        # no psycopg2, no redis
│   └── requirements-dev.txt
│
├── problem-packages/           # Problem workspace
│   └── sum_two_numbers/
│       ├── problem.yaml
│       ├── statement.md
│       └── tests/
│           ├── samples/
│           └── hidden/
│
├── storage/                    # Uploaded files (gitignored)
│   └── submissions/            # Source code snapshots
│
├── docs/
│   ├── architecture.md         # This file
│   └── decision-log.md         # ADR records
│
├── infra/                      # Production Hardening (future)
│   ├── docker-compose.yml
│   └── docker-compose.db.yml
│
├── judge-worker/               # DockerSandboxJudgeRunner (future)
├── .env.example
└── README.md
```

---

## Communication Flows

### Login Flow (MVP)

```
Browser → POST /api/auth/login (Next.js API route)
        → POST /api/v1/auth/login (FastAPI)
          ├── In-memory: check login_attempts[ip]
          ├── SQLite: SELECT user WHERE email=?
          ├── bcrypt verify password
          └── Return JWT
        → Next.js: set httpOnly cookie "access_token"
        → Browser: redirect /dashboard
```

### Submission & Judging Flow (MVP)

```
Browser → POST /api/v1/submissions/ (FastAPI)
        ├── Validate: auth, source not empty
        ├── SQLite: INSERT submission (verdict=PD)
        ├── Save source to storage/submissions/{id}/
        └── Dispatch to LocalSubprocessJudgeRunner (background thread)
              ├── Compile (C++) or skip (Python)
              ├── For each testcase in problem-packages/{code}/tests/hidden/:
              │     subprocess.run(binary, input=testcase.in, timeout=time_limit)
              │     Compare output → AC/WA/TLE/RE
              └── SQLite: UPDATE submission (verdict, testcase_results)

Browser → GET /api/v1/submissions/{id} (polling every 2s)
        → Returns updated verdict when judging complete
```

### Protected Route Flow (MVP)

```
Browser → GET /admin/users
        → Next.js Middleware (Edge Runtime)
          ├── Read "access_token" cookie
          ├── [No token] → redirect /login
          ├── Decode JWT payload
          └── [Role insufficient] → redirect /403
              [Role OK] → forward to FastAPI
                        → FastAPI: verify JWT + in-memory blacklist check
                        → Return 200 or 401/403
```

---

## Local Development Setup

```bash
# Prerequisites: Python 3.12+, Node.js 20+, g++ (optional for C++ judging)

# Backend
cd api-server
pip install -r requirements-dev.txt
python -m app.db.init_db    # creates SQLite DB, runs migrations, seeds data
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd web-app
npm install
npm run dev

# Tests
pytest api-server/tests/ -v
cd web-app && npx vitest --run
```

**Service URLs:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Seed accounts:**

| Email | Password | Role |
|-------|----------|------|
| superadmin@mindx.edu.vn | SuperAdmin@123 | Super_Admin |
| admin@mindx.edu.vn | Admin@123 | Admin |
| teacher@mindx.edu.vn | Teacher@123 | Teacher |
| student@mindx.edu.vn | Student@123 | Student |

---

## Security Considerations (MVP)

- JWT lưu trong httpOnly cookie — không accessible từ JavaScript (chống XSS)
- In-memory token blacklist — logout thực sự vô hiệu hóa token (mất khi restart, chấp nhận được cho local dev)
- bcrypt password hashing
- In-memory rate limiting cho login (10 lần / 15 phút / IP)
- Path traversal protection cho tất cả file upload
- Generic error messages cho login/password-reset (tránh user enumeration)
- **LocalSubprocessJudgeRunner không có sandbox isolation** — chỉ dùng cho trusted local dev; upgrade lên DockerSandboxJudgeRunner cho production

---

## Production Hardening Upgrade Path

| MVP Component | Production Replacement | Effort |
|---------------|----------------------|--------|
| SQLite | PostgreSQL 16 | Medium — thay DATABASE_URL, chạy lại migrations |
| In-memory rate limiter | Redis INCR + EXPIRE | Low — thay rate_limit.py |
| In-memory token blacklist | Redis SET + TTL | Low — thay deps.py blacklist |
| LocalSubprocessJudgeRunner | DockerSandboxJudgeRunner | High — cần Docker, sandbox config |
| Synchronous judging | Redis job queue + worker process | High — tách judge-worker service |
| Local filesystem | S3-compatible object storage | Medium — thay storage layer |
