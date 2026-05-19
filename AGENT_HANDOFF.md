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
5. **`docs/ROUND2_CLOSURE.md`** — Biên bản chốt Round 2 và checklist bàn giao Round 3

---

### Trạng thái hiện tại

**Tiến độ thực tế: ~60% MVP**

| Round | Nội dung | Trạng thái |
|-------|----------|-----------|
| Round 1 | Repository setup + Backend scaffolding | ✅ HOÀN THÀNH |
| Round 2 | User model + Auth core + Frontend foundation + Auth UI | ✅ HOÀN THÀNH |
| Round 3 | Problem domain + Judge runner + Submission flow | 🟡 SẴN SÀNG BẮT ĐẦU |
| Round 4 | Frontend problem/submission pages | 🔴 CHƯA BẮT ĐẦU |
| Round 5 | Tests + full end-to-end verification | 🔴 CHƯA BẮT ĐẦU |

**Những phần vừa chốt xong trong Round 2 closure:**
- Auth backend đã chạy được: `api-server/app/routers/auth.py`
- Users backend đã chạy được: `api-server/app/routers/users.py`
- Next.js auth proxy routes đã có: `web-app/src/app/api/auth/login/route.ts`, `logout/route.ts`
- `LoginForm.tsx` đã hoạt động với redirect theo role
- `AuthGuard.tsx` đã có
- `globals.css` + `layout.tsx` đã được nối đúng → UI có style
- Đã có các page đích sau login: `/dashboard`, `/teacher`, `/admin`
- Đã có `api-server/app/db/init_db.py` để seed local SQLite
- Đã có `start-dev.sh` để khởi động dev environment nhanh

---

### Những gì đã có (không cần làm lại)

**Backend:**
- `app/main.py` — FastAPI app với CORS, routers, `/health` endpoint
- `app/core/config.py` — Settings (pydantic-settings)
- `app/core/security.py` — `hash_password`, `verify_password`, `create_access_token`, `decode_access_token`
- `app/core/deps.py` — `get_current_user`, `require_role`, `blacklist_token`, `is_token_blacklisted`
- `app/core/rate_limit.py` — `check_login_rate_limit`, `record_login_attempt`, `reset_login_attempts`
- `app/db/base.py`, `app/db/session.py` — SQLite engine, `get_db()`
- `app/db/migrations/` — Alembic config + migration `001_create_initial_tables`
- `app/db/init_db.py` — local DB init + seed users/problems
- `app/models/user.py` — `User` ORM + `UserRole`
- `app/models/password_reset_token.py` — `PasswordResetToken` ORM
- `app/schemas/user.py` — `UserBase`, `UserCreate`, `UserRead`, `UserUpdate`
- `app/schemas/auth.py` — `LoginRequest`, `TokenResponse`, `TokenPayload`
- `app/services/auth_service.py` — auth business logic
- `app/routers/auth.py` — login/logout/password reset endpoints
- `app/routers/users.py` — `/me`, list, create, get, patch users

**Frontend:**
- `package.json`, `tsconfig.json`, `tailwind.config.ts`, `next.config.ts`, `postcss.config.js`
- `src/app/layout.tsx` + `src/app/globals.css` — design system + global styles
- `src/middleware.ts` — Edge Runtime RBAC (cookie-based)
- `src/types/` — `auth.ts`, `problem.ts`, `submission.ts`, `index.ts`
- `src/lib/api.ts` — fetch-based API client
- `src/lib/auth.ts` — auth helpers
- `src/components/auth/LoginForm.tsx`
- `src/components/auth/AuthGuard.tsx`
- `src/app/login/page.tsx`
- `src/app/api/auth/login/route.ts`
- `src/app/api/auth/logout/route.ts`
- `src/app/dashboard/page.tsx`
- `src/app/teacher/page.tsx`
- `src/app/admin/page.tsx`

---

### Còn là stub / chưa hoàn tất (ưu tiên tiếp theo)

**Backend domain logic:**
- `app/models/problem.py`
- `app/schemas/problem.py`
- `app/services/problem_service.py`
- `app/routers/problems.py`
- `app/judge/base.py`
- `app/judge/local_runner.py`
- `app/models/submission.py`
- `app/schemas/submission.py`
- `app/services/submission_service.py`
- `app/routers/submissions.py`

**Frontend product pages:**
- forgot-password / reset-password pages còn ở mức chưa hoàn chỉnh
- protected layout dùng chung
- student / teacher / admin dashboard thực tế vẫn là placeholder
- toàn bộ problem pages, editor, submission history pages chưa làm

**Tests / verification:**
- Chưa có backend auth tests
- Chưa có property tests
- Chưa có frontend Vitest setup
- Chưa có full end-to-end verification script

---

### Conventions quan trọng

**Python:**
- SQLAlchemy 2.0: dùng `Mapped[T]` + `mapped_column()`, KHÔNG dùng `Column()` cũ
- UUID: `str(uuid.uuid4())` lưu dưới dạng `String(36)`
- Ưu tiên `datetime.now(timezone.utc)` thay vì `datetime.utcnow()` cho code mới
- Pydantic V2: `model_config = ConfigDict(from_attributes=True)` cho ORM schemas
- bcrypt: `bcrypt==4.0.1` đã pinned
- Auth errors: KHÔNG tiết lộ email có tồn tại hay không

**TypeScript:**
- Path alias: `@/*` → `./src/*`
- API calls qua `lib/api.ts`, không fetch trực tiếp trừ Next.js proxy routes
- Tất cả npm deps phải pinned exact version
- Login redirect theo role hiện được quyết định từ server route `/api/auth/login`

---

### Nhiệm vụ của bạn

**Bắt đầu Round 3 thực sự** theo `tasks.md`, ưu tiên theo thứ tự sau:

1. **Hoàn thiện Problem domain (6.1 → 6.4)**
   - Model, schema, service, router cho problems
2. **Hoàn thiện Judge runner (7.1 → 7.2)**
   - `AbstractJudgeRunner` + `LocalSubprocessJudgeRunner`
3. **Hoàn thiện Submission flow backend (8.1 → 8.4)**
4. Sau đó mới chuyển sang frontend problem/submission pages

**Lưu ý quan trọng:**
- Không rollback các thay đổi Round 2 closure
- Nếu cần sửa `init_db.py`, giữ seed accounts ổn định để tiện verify login
- Nếu cần đổi route frontend, phải đảm bảo middleware + LoginForm + API auth routes vẫn đồng bộ

---

### Lệnh setup để bắt đầu

```bash
# Từ root repo
chmod +x start-dev.sh
./start-dev.sh

# Hoặc chạy tay
cd api-server
pip install -r requirements-dev.txt
python -m app.db.init_db
uvicorn app.main:app --reload --port 8000

cd ../web-app
npm install
npm run dev
```

---

### Seed accounts hiện tại

- `admin@mindx.edu.vn / Admin@123`
- `teacher@mindx.edu.vn / Teacher@123`
- `student1@mindx.edu.vn / Student@123`
- `student2@mindx.edu.vn / Student@123`

---

*Handoff được cập nhật sau bước chốt cuối Round 2. Ngày: 2026-05-19.*
