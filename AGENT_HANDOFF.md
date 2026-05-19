# Agent Handoff Prompt — MindX Online Judge

> Copy toàn bộ nội dung phần **"PROMPT"** bên dưới và paste vào AI Agent mới.

---

## PROMPT

---

Bạn đang tiếp nhận một dự án đang phát triển dở dang. Hãy đọc kỹ context sau trước khi làm bất cứ điều gì.

---

### Dự án là gì?

**MindX Online Judge** — nền tảng judge lập trình nội bộ cho MindX Education. Giáo viên tạo bài tập, upload testcase; học sinh nộp code, nhận kết quả chấm tự động (AC/WA/TLE/RE/CE).

Đây là phiên bản **Local-First MVP** — chạy hoàn toàn trên máy local, không cần Docker, PostgreSQL, hay Redis.

---

### Tài liệu bắt buộc phải đọc (theo thứ tự)

1. **`.kiro/steering/project-context.md`** — Context tổng hợp: trạng thái hiện tại, cấu trúc file, conventions, quy tắc
2. **`.kiro/specs/mindx-online-judge/tasks.md`** — Danh sách task với dependency graph — **SOURCE OF TRUTH** cho tiến độ
3. **`docs/architecture.md`** — Kiến trúc hệ thống, communication flows, setup commands
4. **`.kiro/specs/mindx-online-judge/requirements.md`** — 10 requirements với acceptance criteria chi tiết

---

### Trạng thái hiện tại

**Tiến độ: ~45% MVP**

| Round | Nội dung | Trạng thái |
|-------|----------|-----------|
| Round 1 | Repository setup + Backend scaffolding | ✅ HOÀN THÀNH |
| Round 2 | User model + Auth core (security, deps, rate_limit, auth_service) + Frontend scaffolding | ✅ HOÀN THÀNH |
| Round 3 | Auth routers + Problem model + Auth UI components | 🔴 CHƯA BẮT ĐẦU — **TIẾP THEO** |
| Round 4 | Problem service/router + Judge runner + Submission flow | 🔴 Chưa bắt đầu |
| Round 5 | Seeds + Init script + Backend checkpoint | 🔴 Chưa bắt đầu |
| Round 6–8 | Frontend pages + Tests | 🔴 Chưa bắt đầu |

**Tasks sẵn sàng thực hiện ngay (Wave 5):**
- `5.1` — `api-server/app/routers/auth.py` (login, logout, password-reset endpoints)
- `5.2` — `api-server/app/routers/users.py` (CRUD users)
- `6.1` — `api-server/app/models/problem.py` (Problem ORM model)
- `6.2` — `api-server/app/schemas/problem.py` (Pydantic schemas)
- `12.2` — `web-app/src/components/auth/LoginForm.tsx`
- `12.3` — Next.js API routes cho auth (login/logout)
- `12.4` — `web-app/src/components/auth/AuthGuard.tsx`

---

### Những gì đã có (không cần làm lại)

**Backend:**
- `app/main.py` — FastAPI app với CORS, routers, `/health` endpoint
- `app/core/config.py` — Settings (pydantic-settings)
- `app/core/security.py` — `hash_password`, `verify_password`, `create_access_token`, `decode_access_token`
- `app/core/deps.py` — `get_current_user`, `require_role`, `blacklist_token`, `is_token_blacklisted`
- `app/core/rate_limit.py` — `check_login_rate_limit`, `record_login_attempt`, `reset_login_attempts`
- `app/db/base.py`, `app/db/session.py` — SQLite engine, `get_db()`
- `app/db/migrations/` — Alembic config + migration `001_create_initial_tables` (4 bảng)
- `app/models/user.py` — `User` ORM + `UserRole` enum (SQLAlchemy 2.0 style)
- `app/models/password_reset_token.py` — `PasswordResetToken` ORM
- `app/schemas/user.py` — `UserBase`, `UserCreate`, `UserRead`, `UserUpdate`
- `app/schemas/auth.py` — `LoginRequest`, `TokenResponse`, `TokenPayload`
- `app/services/auth_service.py` — 6 functions: authenticate, create_user, get_by_email/id, password_reset

**Frontend:**
- `package.json`, `tsconfig.json`, `tailwind.config.ts`, `next.config.ts`, `postcss.config.js`
- `src/middleware.ts` — Edge Runtime RBAC (jose.decodeJwt, cookie-based)
- `src/types/` — `auth.ts`, `problem.ts`, `submission.ts`, `index.ts`
- `src/lib/api.ts` — 12 API functions (fetch-based, auto Bearer token)
- `src/lib/auth.ts` — `decodeToken`, `isTokenExpired`, `hasRequiredRole`, `getTokenFromCookie`

**Còn là stub rỗng (cần implement):**
- `app/routers/auth.py`, `users.py`, `problems.py`, `submissions.py`
- `app/models/problem.py`, `submission.py`
- `app/schemas/problem.py`, `submission.py`
- `app/services/problem_service.py`, `submission_service.py`
- `app/judge/local_runner.py` (skeleton chưa implement)
- `web-app/src/app/` (hoàn toàn rỗng)
- `web-app/src/components/` (hoàn toàn rỗng)

---

### Conventions quan trọng

**Python:**
- SQLAlchemy 2.0: dùng `Mapped[T]` + `mapped_column()`, KHÔNG dùng `Column()` cũ
- UUID: `str(uuid.uuid4())` lưu dưới dạng `String(36)`
- Datetime: `datetime.now(timezone.utc)`, KHÔNG dùng `datetime.utcnow()`
- Pydantic V2: `model_config = ConfigDict(from_attributes=True)` cho ORM schemas
- bcrypt: `bcrypt==4.0.1` đã pinned (passlib 1.7.4 không tương thích bcrypt >= 4.1)
- Auth errors: KHÔNG tiết lộ email có tồn tại hay không (generic messages)

**TypeScript:**
- Path alias: `@/*` → `./src/*`
- Import types từ `@/types` (barrel export)
- API calls qua `lib/api.ts`, không fetch trực tiếp
- Tất cả npm deps phải pinned exact version (no `^` or `~`)

---

### Nhiệm vụ của bạn

**Tiếp tục thực hiện Round 3** theo đúng thứ tự dependency trong `tasks.md`.

Quy trình:
1. Đọc `tasks.md` để xác định tasks đang ở trạng thái `ready`
2. Implement từng task theo spec trong `tasks.md` và acceptance criteria trong `requirements.md`
3. Sau mỗi task, verify bằng cách chạy `python -c "from app.xxx import yyy"` hoặc `tsc --noEmit`
4. Cập nhật trạng thái task trong `tasks.md` (thay `[ ]` thành `[x]`)
5. Tiếp tục cho đến khi Round 3 hoàn thành

**Mục tiêu Round 3:** Sau khi xong, có thể chạy `uvicorn app.main:app --reload` và test login API qua Swagger UI tại `http://localhost:8000/docs`, đồng thời frontend có trang login hoạt động.

---

### Lệnh setup để bắt đầu

```bash
# Cài dependencies backend
cd api-server
pip install -r requirements-dev.txt

# Kiểm tra server có khởi động được không
uvicorn app.main:app --reload --port 8000
# Truy cập http://localhost:8000/health → {"status": "ok"}
# Truy cập http://localhost:8000/docs → Swagger UI (các endpoint còn rỗng)

# Frontend (nếu cần)
cd web-app
npm install
```

---

*Handoff được tạo tự động từ Kiro IDE. Ngày: 2026-05-19. Round 2 vừa hoàn thành.*
