# Decision Log — MindX Online Judge

Tài liệu này ghi lại các quyết định kiến trúc quan trọng theo format **Architecture Decision Record (ADR)**.

Mỗi ADR gồm: **Context** — **Decision** — **Consequences**

---

## ADR-001: Chọn FastAPI thay vì Django hoặc NestJS cho Backend

**Ngày**: 2025-01-01 | **Trạng thái**: Accepted

### Context

Backend cần phục vụ: xác thực JWT, RBAC, quản lý bài tập, nhận submission, chấm bài. Các lựa chọn: Django + DRF, NestJS, FastAPI.

### Decision

Chọn **FastAPI**.

1. **Async-first**: ASGI/Starlette, hỗ trợ `async/await` tự nhiên cho I/O-bound workload.
2. **Pydantic integration**: Validation tự động qua type hints, giảm boilerplate.
3. **Auto OpenAPI docs**: Swagger UI tự động từ code.
4. **Python ecosystem**: Cùng ngôn ngữ với judge runner, chia sẻ utilities dễ dàng.
5. **Nhẹ**: Không mang theo admin panel, template engine không cần thiết.

### Consequences

**Tích cực:** Code ngắn gọn, docs luôn đồng bộ, dễ test với pytest + Hypothesis.

**Tiêu cực:** Không có admin panel tích hợp; Alembic cần cấu hình thủ công.

---

## ADR-002: Chọn Next.js thay vì Plain React cho Frontend

**Ngày**: 2025-01-01 | **Trạng thái**: Accepted

### Context

Frontend cần: trang đăng nhập, dashboard theo role, code editor, submission history, teacher/admin management.

### Decision

Chọn **Next.js** (App Router).

1. **Server-side route protection**: Middleware Edge Runtime kiểm tra JWT trước khi render.
2. **API Routes**: Set httpOnly cookie cho JWT — chống XSS tốt hơn localStorage.
3. **App Router**: Server Components, nested layouts, loading/error boundaries.
4. **`output: 'standalone'`**: Sẵn sàng cho Docker deployment khi cần.

### Consequences

**Tích cực:** JWT an toàn trong httpOnly cookie; route protection server-side khó bypass hơn.

**Tiêu cực:** Phức tạp hơn plain React; build time lâu hơn Vite.

---

## ADR-003: Chọn SQLite cho MVP thay vì PostgreSQL

**Ngày**: 2025-01-01 | **Trạng thái**: Accepted

### Context

MVP cần database để lưu users, problems, submissions. Yêu cầu: chạy được ngay không cần cài server riêng. Các lựa chọn: PostgreSQL, MySQL, SQLite.

### Decision

Chọn **SQLite** cho MVP.

1. **Zero setup**: Không cần cài server, không cần Docker — chỉ cần `pip install sqlalchemy`.
2. **File-based**: Database là một file `data/mindx.db` — dễ backup, reset, chia sẻ.
3. **SQLAlchemy compatible**: Cùng ORM code, chỉ thay `DATABASE_URL` khi upgrade.
4. **Alembic migrations**: Hoạt động với SQLite, migration scripts tương thích PostgreSQL.
5. **Đủ cho MVP**: Single-user local dev không cần concurrent write performance của PostgreSQL.

### Consequences

**Tích cực:** Developer mới setup trong < 2 phút; không cần Docker cho dev.

**Tiêu cực:** Không phù hợp cho production multi-user; không có native UUID/ENUM types (dùng String thay thế); concurrent writes bị serialize.

### Upgrade Path: SQLite → PostgreSQL

```bash
# 1. Cài psycopg2-binary
pip install psycopg2-binary==2.9.9

# 2. Thay DATABASE_URL trong .env
DATABASE_URL=postgresql://mindx:password@localhost:5432/mindx_judge

# 3. Chạy lại migrations (Alembic tự detect dialect)
alembic upgrade head

# 4. Chạy seed script
python -m app.db.seeds
```

Lưu ý: SQLite dùng `String(36)` cho UUID và `SAEnum` với `native_enum=False`. Khi migrate sang PostgreSQL, có thể dùng `UUID` native type và `native_enum=True` — cần tạo migration mới.

---

## ADR-004: Chọn LocalSubprocessJudgeRunner cho MVP thay vì Docker Sandbox

**Ngày**: 2025-01-01 | **Trạng thái**: Accepted

### Context

MVP cần chấm bài tự động. Các lựa chọn: Docker sandbox (an toàn nhưng cần Docker), subprocess trực tiếp (đơn giản nhưng không có isolation), external judge service.

### Decision

Chọn **LocalSubprocessJudgeRunner** cho MVP.

1. **Zero dependencies**: Không cần Docker — chỉ cần `g++` và `python3` trên host.
2. **Đủ cho trusted local dev**: MVP chạy trên máy developer, không có malicious code.
3. **Interface abstraction**: `AbstractJudgeRunner` cho phép swap sang `DockerSandboxJudgeRunner` mà không thay đổi business logic.
4. **Nhanh**: Không có container startup overhead.

### Consequences

**Tích cực:** Setup đơn giản; phù hợp cho local dev với trusted users.

**Tiêu cực:** **Không có sandbox isolation** — code học sinh chạy trực tiếp trên host; không giới hạn memory; không chặn network access. **Không dùng cho production.**

### Upgrade Path: LocalSubprocessJudgeRunner → DockerSandboxJudgeRunner

```python
# api-server/app/judge/docker_runner.py (Production Hardening)
class DockerSandboxJudgeRunner(AbstractJudgeRunner):
    """
    Production judge runner — runs code in isolated Docker container.
    
    Security constraints per container:
    - --network none (no network access)
    - --memory {memory_limit_mb}m
    - --cpus 1
    - --pids-limit 1
    - --read-only (except /tmp workdir)
    - --security-opt no-new-privileges
    - Wall time limit = CPU time limit + 2s
    - Output size limit: 64 MB
    """
    def judge(self, submission: Submission) -> None:
        ...
```

Để kích hoạt: thay `LocalSubprocessJudgeRunner` bằng `DockerSandboxJudgeRunner` trong dependency injection của `submissions.py`.

---

## ADR-005: Deferring Docker Compose — Không dùng cho Local Development MVP

**Ngày**: 2025-01-01 | **Trạng thái**: Deferred (không phải Accepted)

### Context

Docker Compose có thể được dùng để chạy toàn bộ stack (Next.js, FastAPI, PostgreSQL, Redis, judge worker) trong containers. Tuy nhiên, điều này tạo ra friction không cần thiết cho MVP.

### Decision

**Không dùng Docker Compose cho local development MVP.** Docker Compose được giữ lại trong `infra/` như một artifact cho Production Hardening.

Lý do defer:
1. **Friction cao**: Developer cần cài Docker Desktop (>4GB), build images lần đầu mất 5-10 phút.
2. **Không cần thiết**: SQLite + subprocess judge không cần containerization.
3. **Hot-reload phức tạp**: Code changes trong container cần volume mounts và restart.
4. **MVP priority**: Ưu tiên "chạy được ngay" hơn "production-like environment".

### Consequences

**Tích cực:** Developer mới setup trong < 5 phút; hot-reload tức thì; không cần Docker Desktop.

**Tiêu cực:** Môi trường dev khác production; cần cài Python và Node.js trực tiếp trên host.

### Upgrade Path: Kích hoạt Docker Compose cho Production

```bash
# Sau khi đã migrate sang PostgreSQL + Redis + DockerSandboxJudgeRunner:
cd infra
cp ../.env.example ../.env
# Điền DB_PASSWORD, SECRET_KEY, etc.
docker compose up --build

# Services:
# - db: PostgreSQL 16 (port 5432)
# - redis: Redis 7 (port 6379)
# - api: FastAPI (port 8000)
# - web: Next.js (port 3000)
# - worker: DockerSandboxJudgeRunner (no exposed port)
```

---

## ADR-006: Chọn In-Memory cho Rate Limiting và Token Blacklist trong MVP

**Ngày**: 2025-01-01 | **Trạng thái**: Accepted (MVP only)

### Context

MVP cần: login rate limiting (10 lần / 15 phút / IP) và token blacklist (logout). Redis là giải pháp production-grade nhưng cần server riêng.

### Decision

Dùng **in-memory Python structures** cho MVP:
- Rate limiting: `defaultdict(list)` với `threading.Lock`
- Token blacklist: `set[str]` (JTI strings)
- Password reset tokens: SQLite table `password_reset_tokens`

### Consequences

**Tích cực:** Zero dependencies; không cần Redis server.

**Tiêu cực:** State mất khi server restart (chấp nhận được cho local dev); không scale ngang (chấp nhận được cho single-process MVP).

### Upgrade Path: In-Memory → Redis

```python
# rate_limit.py — thay implementation:
import redis.asyncio as aioredis

async def check_login_rate_limit(ip: str, redis: aioredis.Redis) -> None:
    key = f"login_attempts:{ip}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 900)
    if count > 10:
        raise HTTPException(429, "LOGIN_RATE_LIMITED")

# deps.py — thay blacklist:
async def blacklist_token(jti: str, ttl: int, redis: aioredis.Redis) -> None:
    await redis.setex(f"token_blacklist:{jti}", ttl, "1")

async def is_token_blacklisted(jti: str, redis: aioredis.Redis) -> bool:
    return await redis.exists(f"token_blacklist:{jti}") > 0
```

---

*Tài liệu này được cập nhật khi có quyết định kiến trúc mới.*
