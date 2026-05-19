# Implementation Plan: MindX Online Judge — Local-First MVP

## Overview

Kế hoạch triển khai cho **Local-First MVP** của MindX Online Judge.

**Nguyên tắc:** Không cần Docker, PostgreSQL, hay Redis. Chạy được ngay với `pip install` + `python -m app.db.init_db` + `uvicorn`.

**Tech Stack MVP:**
- Backend: FastAPI + Python 3.12 + SQLAlchemy + SQLite + Alembic
- Judge: LocalSubprocessJudgeRunner (subprocess trực tiếp trên host)
- Frontend: Next.js + TypeScript + Tailwind CSS
- Tests: pytest + Hypothesis (backend), Vitest + RTL (frontend)

**Production Hardening (không thuộc MVP):** PostgreSQL, Redis, DockerSandboxJudgeRunner, Docker Compose.

---

## Tasks

- [ ] 1. Cập nhật cấu trúc monorepo cho local-first MVP
  - [x] 1.1 Cập nhật cấu trúc thư mục api-server
    - Tạo `api-server/app/judge/` với `__init__.py`, `base.py`, `local_runner.py`
    - Tạo `api-server/data/` (gitignored) cho SQLite database file
    - Tạo `api-server/app/models/problem.py` và `api-server/app/models/submission.py` (placeholder)
    - Tạo `api-server/app/routers/problems.py` và `api-server/app/routers/submissions.py` (placeholder)
    - Tạo `api-server/app/services/problem_service.py` và `api-server/app/services/submission_service.py` (placeholder)
    - Cập nhật `storage/` với thư mục con `submissions/`
    - _Requirements: Phase 0 — Repository Setup_

  - [x] 1.2 Cập nhật `.env.example` cho local-first MVP
    - Xóa `DB_PASSWORD`, `REDIS_URL` khỏi required vars
    - Thêm `DATABASE_URL=sqlite:///./data/mindx.db`
    - Giữ `SECRET_KEY`, `NEXT_PUBLIC_API_URL`, `SMTP_*` (optional cho MVP)
    - Thêm `PROBLEM_PACKAGES_DIR=../problem-packages`
    - Thêm `SUBMISSIONS_DIR=../storage/submissions`
    - _Requirements: Requirement 9_

  - [x] 1.3 Tạo seed problem package
    - Tạo `problem-packages/sum_two_numbers/problem.yaml`
    - Tạo `problem-packages/sum_two_numbers/statement.md`
    - Tạo `problem-packages/sum_two_numbers/tests/samples/01.in` và `01.out`
    - Tạo `problem-packages/sum_two_numbers/tests/hidden/01.in` và `01.out`
    - _Requirements: Requirement 3_

- [ ] 2. Tạo project scaffolding cho api-server (Backend Foundation)
  - [-] 2.1 Cập nhật `api-server/requirements.txt` và `requirements-dev.txt`
    - `requirements.txt`: `fastapi==0.111.0`, `uvicorn[standard]==0.29.0`, `sqlalchemy==2.0.30`, `alembic==1.13.1`, `python-jose[cryptography]==3.3.0`, `passlib[bcrypt]==1.7.4`, `pydantic[email]==2.7.1`, `pydantic-settings==2.2.1`, `python-dotenv==1.0.1`, `python-multipart==0.0.9`, `aiofiles==23.2.1`
    - Xóa `psycopg2-binary` và `redis` khỏi requirements.txt (không cần cho MVP)
    - `requirements-dev.txt`: `pytest==8.2.0`, `pytest-asyncio==0.23.6`, `httpx==0.27.0`, `hypothesis==6.100.1`, `factory-boy==3.3.0`, `faker==24.11.0`
    - _Requirements: Requirement 9_

  - [-] 2.2 Tạo `api-server/app/core/config.py` — Settings
    - Dùng `pydantic-settings` để load từ environment variables
    - Fields: `DATABASE_URL="sqlite:///./data/mindx.db"`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_HOURS=24`, `ALGORITHM="HS256"`, `LOGIN_RATE_LIMIT_ATTEMPTS=10`, `LOGIN_RATE_LIMIT_WINDOW_SECONDS=900`, `PROBLEM_PACKAGES_DIR="../problem-packages"`, `SUBMISSIONS_DIR="../storage/submissions"`
    - _Requirements: 1, 9_

  - [-] 2.3 Tạo `api-server/app/db/base.py` và `api-server/app/db/session.py`
    - `base.py`: `Base = declarative_base()`
    - `session.py`: SQLite engine với `check_same_thread=False`, `SessionLocal`, `get_db()` dependency
    - _Requirements: Requirement 9_

  - [x] 2.4 Tạo `api-server/app/main.py` — FastAPI entry point
    - Khởi tạo FastAPI app với title, version
    - Include routers: auth, users, problems, submissions
    - CORS middleware cho `NEXT_PUBLIC_API_URL`
    - `GET /health` endpoint
    - _Requirements: Requirement 9_

- [x] 3. Triển khai User model và Auth (SQLite)
  - [x] 3.1 Tạo `api-server/app/models/user.py` — SQLAlchemy ORM model cho SQLite
    - `UserRole` enum: `student`, `teacher`, `admin`, `super_admin`
    - `User` model: `id` (String UUID), `name`, `email` (unique, indexed), `password_hash`, `role` (SAEnum), `is_active`, `created_at`, `updated_at`
    - _Requirements: 1, 2_

  - [x] 3.2 Tạo `api-server/app/schemas/user.py` và `api-server/app/schemas/auth.py`
    - `user.py`: `UserBase`, `UserCreate`, `UserRead`, `UserUpdate`
    - `auth.py`: `LoginRequest`, `TokenResponse`, `TokenPayload` (với `jti` field)
    - _Requirements: 1, 2_

  - [x] 3.3 Khởi tạo Alembic và tạo migration đầu tiên
    - Chạy `alembic init app/db/migrations` trong `api-server/`
    - Cấu hình `alembic.ini` và `env.py` để dùng `DATABASE_URL` từ settings
    - Tạo migration `create_initial_tables` tạo bảng `users`, `problems`, `submissions`, `password_reset_tokens`
    - _Requirements: 1, 2, 3, 6_

  - [x] 3.4 Tạo `api-server/app/core/security.py` — Password hashing và JWT
    - `hash_password(plain: str) -> str` — bcrypt
    - `verify_password(plain: str, hashed: str) -> bool`
    - `create_access_token(data: dict, expires_delta=None) -> str` — JWT HS256 với `jti` claim
    - `decode_access_token(token: str) -> dict` — raise HTTPException(401) nếu invalid
    - _Requirements: 1_


- [x] 4. Triển khai In-Memory Rate Limiter và Auth Dependencies
  - [x] 4.1 Tạo `api-server/app/core/rate_limit.py` — In-memory rate limiter
    - Dùng `defaultdict(list)` + `threading.Lock` để lưu login attempts theo IP
    - `check_login_rate_limit(ip: str) -> None` — raise HTTPException(429) nếu > 10 lần trong 900s
    - `record_login_attempt(ip: str) -> None`
    - `reset_login_attempts(ip: str) -> None`
    - Comment rõ upgrade path: thay bằng Redis INCR + EXPIRE cho production
    - _Requirements: 1.5_

  - [x] 4.2 Tạo `api-server/app/core/deps.py` — Auth dependencies
    - `get_current_user(token, db) -> User` — decode JWT, kiểm tra in-memory blacklist
    - `require_role(*roles: UserRole)` — factory trả về dependency function
    - In-memory token blacklist: `_blacklisted_jtis: set[str]` với `blacklist_token()` và `is_token_blacklisted()`
    - Comment upgrade path: thay blacklist bằng Redis SET + TTL
    - _Requirements: 2_

  - [x] 4.3 Tạo `api-server/app/services/auth_service.py`
    - `authenticate_user(email, password, db) -> User | None`
    - `create_user(data: UserCreate, db) -> User`
    - `get_user_by_email(email, db) -> User | None`
    - `get_user_by_id(user_id, db) -> User | None`
    - `create_password_reset_token(user_id, db) -> str` — lưu vào bảng `password_reset_tokens` SQLite, log token ra console
    - `confirm_password_reset(token, new_password, db) -> bool`
    - _Requirements: 1, 2_


- [ ] 5. Triển khai Auth Router và Users Router
  - [x] 5.1 Tạo `api-server/app/routers/auth.py` — Auth endpoints
    - `POST /api/v1/auth/login`: check rate limit, verify credentials, trả về TokenResponse; reset counter sau login thành công; generic error khi sai credentials
    - `POST /api/v1/auth/logout`: thêm `jti` vào in-memory blacklist
    - `POST /api/v1/auth/password-reset/request`: tạo token, lưu SQLite, log ra console; luôn trả về cùng response
    - `POST /api/v1/auth/password-reset/confirm`: validate token từ SQLite, hash mật khẩu mới, cập nhật DB, đánh dấu token đã dùng
    - _Requirements: 1_

  - [x] 5.2 Tạo `api-server/app/routers/users.py` — Users endpoints
    - `GET /api/v1/users/me` — min role: Student
    - `GET /api/v1/users/` — min role: Admin
    - `POST /api/v1/users/` — min role: Admin; chặn gán `super_admin` nếu actor là Admin
    - `GET /api/v1/users/{user_id}` — min role: Admin
    - `PATCH /api/v1/users/{user_id}` — min role: Admin; chặn role escalation
    - _Requirements: 2_

  - [ ]* 5.3 Viết property tests cho security (Property 1 & 2)
    - **Property 1**: `@given(password=st.text(min_size=1, max_size=72))` — hash round-trip
    - **Property 2**: `@given(user_id=st.uuids(), role=st.sampled_from([...]))` — JWT round-trip
    - _Validates: Requirements 1.1_

  - [ ]* 5.4 Viết unit tests cho auth endpoints
    - Login thành công → 200 + access_token
    - Login sai password → 401 generic message
    - Logout → token blacklisted → 401 on next request
    - Password reset request với email không tồn tại → cùng response
    - _Requirements: 1_


- [ ] 6. Triển khai Problem model, service, và router
  - [~] 6.1 Tạo `api-server/app/models/problem.py` — SQLAlchemy ORM model
    - Fields: `id`, `code` (unique), `title`, `statement_md`, `time_limit_ms`, `memory_limit_mb`, `allowed_languages` (JSON string), `scoring_mode`, `is_visible`, `is_archived`, `package_path`, `created_by`, `created_at`, `updated_at`
    - _Requirements: 3_

  - [~] 6.2 Tạo `api-server/app/schemas/problem.py` — Pydantic schemas
    - `ProblemCreate`, `ProblemRead`, `ProblemUpdate`
    - `ProblemYaml` — schema cho parse/serialize `problem.yaml`
    - _Requirements: 3_

  - [~] 6.3 Tạo `api-server/app/services/problem_service.py`
    - `create_problem(data, db) -> Problem`
    - `get_problem(problem_id, db) -> Problem | None`
    - `list_problems(db, visible_only=True) -> list[Problem]`
    - `update_problem(problem_id, data, db) -> Problem`
    - `archive_problem(problem_id, db) -> Problem`
    - `parse_problem_yaml(path: Path) -> ProblemYaml` — validate required fields
    - `serialize_problem_yaml(problem: ProblemYaml, path: Path) -> None`
    - _Requirements: 3_

  - [~] 6.4 Tạo `api-server/app/routers/problems.py` — Problems endpoints
    - `GET /api/v1/problems/` — Student+: danh sách visible problems
    - `POST /api/v1/problems/` — Teacher+: tạo problem, tạo thư mục package
    - `GET /api/v1/problems/{id}` — Student+: chi tiết problem
    - `PATCH /api/v1/problems/{id}` — Teacher+: cập nhật
    - `DELETE /api/v1/problems/{id}` — Teacher+: archive
    - `POST /api/v1/problems/{id}/statement` — Teacher+: upload statement file (`.md`, `.txt`, `.docx`, `.pdf`)
    - `POST /api/v1/problems/{id}/testcases` — Teacher+: upload testcase ZIP
    - `POST /api/v1/problems/{id}/testcases/pair` — Teacher+: upload cặp `.in`/`.out`
    - _Requirements: 3, 4_

  - [ ]* 6.5 Viết property test cho problem.yaml round-trip (Property 5)
    - `@given(...)` generate valid ProblemYaml objects, serialize rồi parse lại, assert equal
    - _Validates: Requirement 3.4_


- [ ] 7. Triển khai LocalSubprocessJudgeRunner
  - [~] 7.1 Tạo `api-server/app/judge/base.py` — Abstract interface
    - `AbstractJudgeRunner` ABC với method `judge(submission: Submission) -> None`
    - `TestcaseVerdict` dataclass: `index`, `verdict`, `runtime_ms`, `is_hidden`
    - _Requirements: 6_

  - [~] 7.2 Tạo `api-server/app/judge/local_runner.py` — LocalSubprocessJudgeRunner
    - Compile C++17/C++20 bằng `g++`, Python 3 không cần compile
    - Chạy từng testcase bằng `subprocess.run(..., timeout=time_limit_s, capture_output=True)`
    - So sánh output: strip trailing whitespace mỗi dòng, exact match → AC; mismatch → WA
    - Timeout → TLE; non-zero exit code → RE; compile fail → CE (truncate 4KB)
    - Final verdict priority: TLE > RE > WA > AC
    - Chạy trong background thread (ThreadPoolExecutor) để không block API
    - Dọn dẹp workdir sau khi chấm xong
    - Comment rõ: không có sandbox isolation — upgrade path là DockerSandboxJudgeRunner
    - _Requirements: 6_

  - [ ]* 7.3 Viết unit tests cho LocalSubprocessJudgeRunner
    - Test AC: code đúng với testcase đơn giản (sum two numbers)
    - Test WA: code sai output
    - Test TLE: code vòng lặp vô hạn với timeout ngắn
    - Test CE: code C++ syntax error
    - Test RE: code Python raise exception
    - _Requirements: 6_

  - [ ]* 7.4 Viết property test cho verdict consistency (Property 6)
    - Assert: nếu tất cả testcases AC → final verdict AC
    - Assert: nếu có bất kỳ TLE → final verdict TLE
    - _Validates: Requirement 6.9_


- [ ] 8. Triển khai Submission model, service, và router
  - [~] 8.1 Tạo `api-server/app/models/submission.py` — SQLAlchemy ORM model
    - Fields: `id`, `problem_id`, `user_id`, `language`, `source_path`, `verdict` (default PD), `score`, `compile_error`, `testcase_results` (JSON text), `judged_at`, `created_at`
    - _Requirements: 5, 7_

  - [~] 8.2 Tạo `api-server/app/schemas/submission.py` — Pydantic schemas
    - `SubmissionCreate`: `problem_id`, `language`, `source_code`
    - `TestcaseResult`: `index`, `verdict`, `runtime_ms`, `is_hidden`
    - `SubmissionRead`: full submission info với testcase_results (hidden testcases ẩn output)
    - _Requirements: 5, 7_

  - [~] 8.3 Tạo `api-server/app/services/submission_service.py`
    - `create_submission(data, user_id, db) -> Submission` — lưu source code vào `SUBMISSIONS_DIR/{id}/`, tạo record PD
    - `get_submission(submission_id, db) -> Submission | None`
    - `list_submissions(user_id, db, page, page_size=25) -> list[Submission]`
    - `list_all_submissions(db, page, page_size=50) -> list[Submission]` — Admin only
    - `update_verdict(submission_id, verdict, results, db) -> None`
    - _Requirements: 5, 7_

  - [~] 8.4 Tạo `api-server/app/routers/submissions.py` — Submissions endpoints
    - `POST /api/v1/submissions/` — Student+: nộp bài, validate source không rỗng, dispatch judge job
    - `GET /api/v1/submissions/` — Student: lịch sử của mình (25/page)
    - `GET /api/v1/submissions/{id}` — Student: chi tiết (ẩn hidden testcase output)
    - `GET /api/v1/submissions/admin/all` — Admin+: tất cả submissions (50/page)
    - _Requirements: 5, 7_

  - [ ]* 8.5 Viết unit tests cho submission flow
    - Test submit với source rỗng → 400
    - Test submit hợp lệ → 201 + verdict PD
    - Test GET submission của người khác → 403
    - Test hidden testcase output không xuất hiện trong response của Student
    - _Requirements: 5, 7_


- [ ] 9. Seed data và setup script
  - [x] 9.1 Tạo `api-server/app/db/init_db.py` — Seed users và seed problem
    - 4 seed users: Super Admin, Admin MindX, Giáo viên A, Học sinh B
    - `run_seeds(db)` — kiểm tra email chưa tồn tại trước khi insert
    - Import seed problem từ `problem-packages/sum_two_numbers/` vào DB
    - _Requirements: 9_

  - [x] 9.2 Tạo startup script `start-dev.sh` — Unified dev environment
    - Tạo thư mục `data/` nếu chưa có
    - Chạy `alembic upgrade head`
    - Gọi `run_seeds()`
    - In hướng dẫn ra console: URL, seed accounts, lệnh chạy server
    - Chạy được bằng `python -m app.db.init_db`
    - _Requirements: 9_

  - [~] 9.3 Cập nhật `README.md` — Quick start guide
    - Prerequisites: Python 3.12+, Node.js 20+, g++ (optional cho C++)
    - Setup commands: `pip install -r requirements-dev.txt`, `python -m app.db.init_db`, `uvicorn app.main:app --reload`
    - Seed accounts table
    - Production Hardening upgrade path summary
    - _Requirements: 9_


- [~] 10. Checkpoint — Backend MVP hoàn chỉnh
  - Chạy `python -m app.db.init_db` — DB tạo thành công, 4 seed users, seed problem
  - Chạy `uvicorn app.main:app --reload` — server khởi động tại localhost:8000
  - Kiểm tra `GET /health` → 200
  - Kiểm tra login với 4 seed accounts → JWT trả về đúng
  - Kiểm tra Student không truy cập được `/api/v1/users/` → 403
  - Chạy `pytest api-server/tests/ -v` — tất cả tests pass
  - Hỏi user nếu có vấn đề phát sinh.

- [x] 11. Tạo project scaffolding cho web-app (Frontend Foundation)
  - [x] 11.1 Tạo `web-app/package.json` với dependencies
    - `next`, `react`, `react-dom`, `typescript`, `tailwindcss`, `@types/react`, `@types/node`
    - `jose` (JWT decode), `react-hook-form`, `zod`, `@hookform/resolvers`
    - `@monaco-editor/react` (code editor)
    - _Requirements: 5_

  - [x] 11.2 Tạo config files: `tsconfig.json`, `tailwind.config.ts`, `next.config.ts`
    - `tsconfig.json`: path aliases `@/*` → `./src/*`
    - `next.config.ts`: `output: 'standalone'` (cho future Docker)
    - _Requirements: 5_

  - [x] 11.3 Tạo `web-app/src/types/` — TypeScript type definitions
    - `auth.ts`: `UserRole`, `User`, `TokenPayload`, `LoginRequest`, `LoginResponse`
    - `problem.ts`: `Problem`, `ProblemCreate`
    - `submission.ts`: `Submission`, `SubmissionCreate`, `TestcaseResult`, `Verdict`
    - _Requirements: 2, 5, 6_

  - [x] 11.4 Tạo `web-app/src/lib/api.ts` — API client
    - `apiClient` với base URL từ `NEXT_PUBLIC_API_URL`
    - `login()`, `logout()`, `requestPasswordReset()`, `confirmPasswordReset()`
    - `getProblems()`, `getProblem(id)`, `createProblem()`, `uploadStatement()`, `uploadTestcases()`
    - `submitCode()`, `getSubmissions()`, `getSubmission(id)`
    - Auto-attach `Authorization: Bearer <token>` từ cookie
    - _Requirements: 1, 5, 7_

  - [x] 11.5 Tạo `web-app/src/lib/auth.ts` — Auth helper utilities
    - `decodeToken(token) -> TokenPayload | null` dùng `jose`
    - `isTokenExpired(payload) -> boolean`
    - `hasRequiredRole(role, pathname) -> boolean`
    - _Requirements: 2_


- [ ] 12. Triển khai Next.js middleware và auth components
  - [x] 12.1 Tạo `web-app/src/middleware.ts` — Server-side route protection
    - Edge Runtime: đọc `access_token` cookie, decode JWT payload
    - Không có token + protected route → redirect `/login`
    - Role không đủ quyền → redirect `/403`
    - _Requirements: 2_

  - [x] 12.2 Tạo `web-app/src/components/auth/LoginForm.tsx`
    - `react-hook-form` + `zod` validation
    - Submit → Next.js API route `/api/auth/login` → set httpOnly cookie
    - Toast error khi API lỗi; redirect dashboard sau login thành công
    - _Requirements: 1_

  - [x] 12.3 Tạo Next.js API routes cho auth
    - `web-app/src/app/api/auth/login/route.ts` — forward tới FastAPI, set httpOnly cookie
    - `web-app/src/app/api/auth/logout/route.ts` — gọi FastAPI logout, xóa cookie
    - _Requirements: 1_

  - [x] 12.4 Tạo `web-app/src/components/auth/AuthGuard.tsx`
    - Client-side HOC kiểm tra token expiry
    - Token hết hạn → redirect `/login`
    - _Requirements: 1, 2_

- [ ] 13. Triển khai các trang Auth và Dashboard
  - [x] 13.1 Tạo auth pages
    - `(auth)/login/page.tsx` — render LoginForm
    - `(auth)/forgot-password/page.tsx` — form nhập email, luôn hiển thị cùng thông báo
    - `(auth)/reset-password/page.tsx` — đọc token từ URL, form mật khẩu mới
    - _Requirements: 1_

  - [x] 13.2 Tạo protected layout và dashboard pages
    - `(protected)/layout.tsx` — kiểm tra cookie, redirect `/login` nếu không có
    - `(protected)/dashboard/page.tsx` — redirect theo role
    - `(protected)/student/dashboard/page.tsx` — "Chào mừng [name]! Role: Student" + nút Logout
    - `(protected)/teacher/dashboard/page.tsx` — "Chào mừng [name]! Role: Teacher" + nút Logout
    - `(protected)/admin/dashboard/page.tsx` — "Chào mừng [name]! Role: Admin" + nút Logout
    - `403/page.tsx` — "Bạn không có quyền truy cập" + link về dashboard
    - _Requirements: 2_

  - [~] 13.3 Tạo shared layout components
    - `components/layout/Navbar.tsx` — logo, tên user, role badge, nút Logout
    - `components/layout/DashboardLayout.tsx` — sidebar placeholder + children
    - _Requirements: 8_


- [ ] 14. Triển khai Problem pages (Teacher + Student)
  - [~] 14.1 Tạo Teacher problem management pages
    - `(protected)/teacher/problems/page.tsx` — danh sách problems của teacher
    - `(protected)/teacher/problems/new/page.tsx` — form tạo problem mới (title, code, limits, languages)
    - `(protected)/teacher/problems/[id]/edit/page.tsx` — chỉnh sửa problem
    - `(protected)/teacher/problems/[id]/testcases/page.tsx` — upload statement + testcase ZIP/pairs
    - _Requirements: 4, 8_

  - [~] 14.2 Tạo Student problem pages
    - `(protected)/student/problems/page.tsx` — danh sách visible problems
    - `(protected)/student/problems/[id]/page.tsx` — problem detail: statement, constraints, sample testcases, code editor
    - _Requirements: 3, 5_

  - [~] 14.3 Tạo `components/editor/CodeEditor.tsx` — Monaco Editor wrapper
    - Hỗ trợ language switching (python, cpp)
    - File upload button: load `.py`/`.cpp` vào editor
    - Reject file > 64KB với error message
    - _Requirements: 5_

  - [~] 14.4 Tạo `components/editor/SubmitButton.tsx` và submission flow
    - Submit button → POST `/api/v1/submissions/`
    - Hiển thị verdict PD → polling mỗi 2s → cập nhật khi có kết quả
    - Hiển thị `VerdictBadge` (AC=green, WA=red, TLE=orange, RE=purple, CE=gray)
    - _Requirements: 5, 6, 7_

- [ ] 15. Triển khai Submission History pages
  - [~] 15.1 Tạo `(protected)/student/problems/[id]/submissions/page.tsx`
    - Danh sách submissions của student cho problem này (25/page)
    - Mỗi row: verdict badge, language, thời gian nộp
    - _Requirements: 7_

  - [~] 15.2 Tạo `(protected)/student/submissions/[id]/page.tsx` — Submission detail
    - Verdict, language, thời gian, compile error (nếu CE)
    - Per-testcase results: index, verdict, runtime (ẩn hidden testcase output)
    - _Requirements: 7_

  - [~] 15.3 Tạo `(protected)/admin/submissions/page.tsx` — Admin view
    - Tất cả submissions (50/page), filter theo problem/user
    - _Requirements: 8_


- [ ] 16. Viết frontend tests
  - [~] 16.1 Cài đặt testing framework
    - Thêm vào `package.json`: `vitest`, `@vitejs/plugin-react`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `jsdom`
    - Tạo `web-app/vitest.config.ts` với environment `jsdom`
    - Tạo `web-app/src/test/setup.ts`
    - _Requirements: 9_

  - [ ]* 16.2 Viết unit tests cho `LoginForm`
    - Validation error khi submit rỗng
    - Error khi email không hợp lệ
    - Gọi `api.login()` với đúng credentials
    - Toast error khi API lỗi
    - _Requirements: 1_

  - [ ]* 16.3 Viết unit tests cho `auth.ts` utilities
    - `decodeToken` với valid JWT → payload đúng
    - `decodeToken` với invalid token → null
    - `isTokenExpired` với token hết hạn → true
    - `hasRequiredRole` cho từng role/route combination
    - _Requirements: 2_

  - [ ]* 16.4 Viết unit tests cho `CodeEditor`
    - Hiển thị editor với đúng language mode
    - File upload > 64KB → error message
    - File upload hợp lệ → content load vào editor
    - _Requirements: 5_

- [~] 17. Checkpoint cuối — Toàn bộ MVP hoạt động
  - Chạy `python -m app.db.init_db` — setup thành công không cần Docker
  - Chạy `uvicorn app.main:app --reload` + `npm run dev` — cả hai khởi động
  - Đăng nhập với 4 seed accounts, mỗi user thấy đúng dashboard
  - Teacher tạo problem, upload testcase ZIP
  - Student xem problem, submit code Python → nhận AC/WA/TLE/RE/CE
  - Student xem submission history và detail
  - Admin xem tất cả submissions
  - Chạy `pytest api-server/tests/ -v` — tất cả tests pass
  - Chạy `npx vitest --run` trong `web-app/` — tất cả tests pass
  - Hỏi user nếu có vấn đề phát sinh.


---

## Notes

- Tasks đánh dấu `*` là optional — có thể bỏ qua để đạt MVP nhanh hơn.
- **Không có Docker, PostgreSQL, hay Redis trong bất kỳ task nào của MVP.**
- Production Hardening (Docker, PostgreSQL, Redis, DockerSandboxJudgeRunner) được document trong `docs/decision-log.md` nhưng không nằm trong task list này.
- Checkpoint tasks (10, 17) đảm bảo validation tăng dần.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3"] },
    { "id": 1, "tasks": ["2.1", "2.2", "2.3", "2.4"] },
    { "id": 2, "tasks": ["3.1", "3.2", "11.1", "11.2"] },
    { "id": 3, "tasks": ["3.3", "3.4", "11.3", "11.4", "11.5"] },
    { "id": 4, "tasks": ["4.1", "4.2", "4.3", "12.1"] },
    { "id": 5, "tasks": ["5.1", "5.2", "6.1", "6.2", "12.2", "12.3", "12.4"] },
    { "id": 6, "tasks": ["5.3", "5.4", "6.3", "6.4", "7.1", "13.1", "13.2", "13.3"] },
    { "id": 7, "tasks": ["6.5", "7.2", "8.1", "8.2", "14.1", "14.2", "14.3"] },
    { "id": 8, "tasks": ["7.3", "7.4", "8.3", "8.4", "14.4"] },
    { "id": 9, "tasks": ["8.5", "9.1", "15.1", "15.2", "15.3"] },
    { "id": 10, "tasks": ["9.2", "9.3", "16.1"] },
    { "id": 11, "tasks": ["16.2", "16.3", "16.4"] },
    { "id": 12, "tasks": ["10"] },
    { "id": 13, "tasks": ["17"] }
  ]
}
```
