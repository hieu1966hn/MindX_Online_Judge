# Biên bản chốt Round 2 — MindX Online Judge (MVP)

**Ngày chốt:** 2026-05-19
**Trạng thái:** ✅ HOÀN THÀNH (Đã vượt tiến độ dự kiến, cover một phần Round 3/5/6)

## 1. Kết quả đạt được (Checklist)

### A. Auth & Security (Backend)
- [x] **Auth Router:** Đã triển khai đầy đủ endpoints login, logout, password-reset.
- [x] **Users Router:** Đã triển khai CRUD users với phân quyền (Admin/Student/Teacher).
- [x] **Security Core:** Hashing bcrypt, JWT HS256 với JTI blacklisting (in-memory).
- [x] **Rate Limiting:** In-memory rate limiter bảo vệ login (10 attempts / 15 mins).

### B. Frontend Scaffolding & Auth UI
- [x] **Design System:** Tailwind CSS nối đúng vào `globals.css` với palette Technical Blue.
- [x] **Auth Proxy:** Next.js API routes (`/api/auth/login`, `/logout`) proxy tới FastAPI và quản lý HttpOnly cookie.
- [x] **Login UI:** `LoginForm` hoàn chỉnh với validation và thông báo lỗi.
- [x] **Role-based Redirect:** Sau login, user được chuyển đúng về `/admin`, `/teacher`, hoặc `/dashboard`.
- [x] **Auth Guards:** `middleware.ts` (server-side) và `AuthGuard.tsx` (client-side) hoạt động đồng bộ.
- [x] **Placeholder Pages:** Đã tạo các dashboard rỗng để tránh 404 sau khi login.

### C. Developer Experience (DX)
- [x] **Database Seed:** Script `init_db.py` tự động tạo bảng và nạp 4 tài khoản test.
- [x] **Startup Script:** `start-dev.sh` tại root giúp khởi động cả project bằng 1 lệnh.
- [x] **Git Clean:** `.gitignore` đã cover `tsconfig.tsbuildinfo`, SQLite DB và các file rác OS.

## 2. Các file quan trọng nhất đã bàn giao

| File | Chức năng |
|------|-----------|
| `start-dev.sh` | Lệnh khởi động nhanh (Root) |
| `api-server/app/routers/auth.py` | Auth API endpoints |
| `api-server/app/db/init_db.py` | Init & Seed SQLite |
| `web-app/src/app/globals.css` | Giao diện gốc (Design System) |
| `web-app/src/middleware.ts` | Bảo vệ route server-side |
| `web-app/src/app/api/auth/login/route.ts` | Quản lý HttpOnly Cookie |

## 3. Lưu ý bàn giao cho Round 3

### 🟡 Vấn đề cần chú ý
1. **Cookie Access:** Frontend KHÔNG THỂ đọc token trực tiếp từ cookie (HttpOnly). Phải dựa vào logic server-side hoặc gọi `/api/v1/users/me`.
2. **Datetime:** Project đang chuyển dịch dần sang `timezone.utc`. Các model mới trong Round 3 nên tuân thủ điều này.
3. **Roles:** Cẩn thận khi sửa `UserRole` enum, vì nó được map cứng trong cả Backend (SAEnum) và Frontend (Enum).

### 🚀 Mục tiêu Round 3
Tiếp tục triển khai **Problem Domain**:
1. ORM Model cho Problem & Submission.
2. Logic chấm bài (Judge Runner) sử dụng Subprocess.
3. API CRUD bài tập và nộp bài.

---
*Tài liệu này được tạo tự động bởi Antigravity Agent để đánh dấu mốc hoàn thành giai đoạn 2.*
