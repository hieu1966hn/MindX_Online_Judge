# Requirements Document

## Introduction

MindX Online Judge là nền tảng judge lập trình nội bộ dành cho MindX. Hệ thống cho phép giáo viên tạo và quản lý bài tập lập trình, upload testcase, và học sinh nộp bài để nhận kết quả chấm tự động.

**Triết lý MVP local-first:** Phiên bản đầu tiên chạy hoàn toàn trên máy local mà không cần Docker, PostgreSQL, hay Redis. Database là SQLite, storage là local filesystem, judge là `LocalSubprocessJudgeRunner` chạy trực tiếp trên host. Docker, PostgreSQL, Redis, và sandbox isolation được giữ lại như các bước nâng cấp tùy chọn trong giai đoạn Production Hardening.

---

## Glossary

- **System**: Nền tảng MindX Online Judge.
- **Judge**: Engine chấm bài tự động.
- **LocalSubprocessJudgeRunner**: Bộ chấm bài MVP — chạy code học sinh trực tiếp bằng `subprocess` trên host, áp dụng timeout và so sánh output cơ bản.
- **DockerSandboxJudgeRunner**: Bộ chấm bài nâng cao (Production Hardening) — chạy code trong Docker container cô lập với đầy đủ resource limits.
- **Submission**: Một lần nộp bài của Student cho một Problem.
- **Verdict**: Kết quả chấm bài: AC, WA, TLE, RE, CE.
- **Problem**: Bài tập lập trình với statement, constraints, time limit, và testcase set.
- **Testcase**: Một cặp input/output dùng để đánh giá Submission.
- **Problem_Package**: Cấu trúc thư mục chuẩn lưu trữ một Problem trên filesystem.
- **problem.yaml**: File metadata máy đọc được của một Problem_Package.
- **Contest**: Sự kiện thi có thời gian giới hạn.
- **Scoreboard**: Bảng xếp hạng của Contest.
- **Course**: Đơn vị học tập nhóm nhiều ClassGroup.
- **ClassGroup**: Nhóm học sinh được giao cho một Teacher.
- **Role**: Cấp độ quyền hạn: Student, Teacher, Admin, Super_Admin.
- **EARS**: Easy Approach to Requirements Syntax — cú pháp dùng cho acceptance criteria.
- **AC**: Accepted.
- **WA**: Wrong Answer.
- **TLE**: Time Limit Exceeded.
- **RE**: Runtime Error.
- **CE**: Compilation Error.
- **PD**: Pending (đang chờ chấm).

---

## Requirements

---

### Requirement 1: User Authentication

**User Story:** As a User, I want to log in with my credentials, so that I can access the platform with my assigned role and permissions.

#### Acceptance Criteria

1. WHEN a User submits a valid email and password, THE System SHALL authenticate the User and issue a session token valid for 24 hours.
2. WHEN a User submits an invalid email or password, THE System SHALL return a generic authentication error message without revealing which field is incorrect.
3. WHEN an authenticated User's session token expires, THE System SHALL require the User to log in again before accessing any protected resource.
4. WHEN a User requests a password reset, THE System SHALL generate a reset token stored locally (in the SQLite database or a local file) valid for 60 minutes; in the MVP, the reset link SHALL be printed to the server log instead of sent via email.
5. WHEN a User submits more than 10 failed login attempts within 15 minutes from the same IP address, THE System SHALL temporarily block further login attempts from that IP for 15 minutes; in the MVP, this counter SHALL be stored in-memory or in SQLite (not Redis).
6. WHEN a User requests a password reset for an email address that is not registered, THE System SHALL return the same confirmation response as for a registered address without revealing whether the address exists.

---

### Requirement 2: Role-Based Access Control

**User Story:** As an Admin, I want users to have role-based permissions, so that Students cannot access teacher or admin functionality.

#### Acceptance Criteria

1. THE System SHALL assign exactly one Role to each User at account creation time; valid roles are Student, Teacher, Admin, and Super_Admin.
2. WHEN a Student attempts to access an Admin, Teacher, or Super_Admin route, THE System SHALL return an HTTP 403 response.
3. WHEN a Teacher attempts to access an Admin or Super_Admin route, THE System SHALL return an HTTP 403 response.
4. WHEN a Super_Admin accesses any System route, THE System SHALL process the request without returning an HTTP 403 response.
5. WHEN an Admin creates a new User account, THE Admin SHALL be able to assign any Role except Super_Admin; IF the Admin attempts to assign the Super_Admin role, THE System SHALL return an HTTP 403 response.
6. WHEN an unauthenticated request is made to any protected route, THE System SHALL return an HTTP 401 response.

---

### Requirement 3: Problem Package Structure

**User Story:** As a Teacher, I want problems to follow a consistent on-disk structure, so that they can be reliably imported, exported, and validated.

#### Acceptance Criteria

1. THE System SHALL store every Problem as a Problem_Package directory with the structure: `problem.yaml`, `statement.md`, `tests/samples/`, `tests/hidden/`.
2. THE System SHALL parse `problem.yaml` files conforming to the defined schema into Problem objects; required fields are: `code`, `title`, `time_limit_ms` (positive integer ≥ 100), `memory_limit_mb` (positive integer ≥ 1), `allowed_languages`, `scoring_mode`.
3. IF a required field is missing from `problem.yaml`, THE System SHALL return a structured validation error identifying each missing field.
4. FOR ALL valid Problem objects, parsing a `problem.yaml` then serializing it then parsing it again SHALL produce a Problem object with field values equal to those of the original parsed object (round-trip property).
5. THE System SHALL validate that every testcase file name matches the pattern `NN.in` / `NN.out` where `NN` is a zero-padded two-digit integer in the range 01–99.
6. THE System SHALL ensure that hidden testcase output files are never included in any API response accessible to Students.

---

### Requirement 4: Problem Statement and Testcase Upload

**User Story:** As a Teacher, I want to upload problem statement files and testcase pairs, so that I can create problems without writing raw YAML by hand.

#### Acceptance Criteria

1. WHEN a Teacher uploads a problem statement file (`.md`, `.txt`, `.docx`, or `.pdf`), THE System SHALL extract the text content and store it as `statement.md` in the Problem_Package directory.
2. WHEN a Teacher uploads a testcase ZIP, THE System SHALL validate that every `.in` file has a matching `.out` file with the same base name and that the ZIP contains at least one matched pair.
3. IF a testcase ZIP contains a path with `../` sequences, THE System SHALL reject the upload and return a path traversal error.
4. IF a testcase ZIP contains a file with extension `.exe`, `.sh`, `.bat`, `.bin`, or `.cmd`, THE System SHALL reject the upload and identify the offending file.
5. WHEN a valid testcase ZIP is accepted, THE System SHALL extract the testcase pairs into the Problem_Package `tests/` directory on the local filesystem.
6. IF the total uncompressed size of a testcase ZIP exceeds 200 MB, THE System SHALL reject the upload before extracting any files.
7. WHEN a Teacher uploads individual testcase pairs (one `.in` and one `.out` file at a time), THE System SHALL append the pair to the Problem_Package `tests/hidden/` directory with the next available zero-padded two-digit index.

---

### Requirement 5: Online Code Editor and Submission

**User Story:** As a Student, I want to write and submit code directly in the browser, so that I can solve problems without installing a local development environment.

#### Acceptance Criteria

1. THE System SHALL embed a code editor on the Problem submission page with syntax highlighting for Python 3, C++17, and C++20.
2. WHEN a Student selects a language, THE editor SHALL switch to the corresponding syntax highlighting mode.
3. WHEN a Student uploads a source file with a `.py` or `.cpp` extension, THE System SHALL load the file content into the editor, replacing the current content.
4. IF a Student uploads a source file larger than 64 KB, THE System SHALL reject the upload and display an error message.
5. WHEN a Student clicks the submit button with a non-empty editor, THE System SHALL create a Submission record with status PD and pass it to the LocalSubprocessJudgeRunner within 2 seconds.
6. WHEN a Student clicks the submit button with an empty editor and no uploaded file, THE System SHALL reject the submission and display a validation error.
7. THE System SHALL store an immutable snapshot of the submitted source code at the time of submission.

---

### Requirement 6: Local Judge Execution

**User Story:** As a Student, I want my submitted code to be judged automatically, so that I receive an AC/WA/TLE/RE/CE verdict without waiting for a human reviewer.

#### Acceptance Criteria

1. THE LocalSubprocessJudgeRunner SHALL execute each Submission by running the compiled binary or interpreter directly on the host using Python `subprocess`.
2. WHEN a C++ Submission is received, THE LocalSubprocessJudgeRunner SHALL compile the source using `g++ -std=c++17 -O2 main.cpp -o main` for C++17 or `g++ -std=c++20 -O2 main.cpp -o main` for C++20 before execution.
3. WHEN a Python 3 Submission is received, THE LocalSubprocessJudgeRunner SHALL execute the source using `python3 main.py` without a separate compilation step.
4. THE LocalSubprocessJudgeRunner SHALL enforce the Problem's time limit using `subprocess` timeout; IF the process exceeds the time limit, THE runner SHALL terminate it and assign verdict TLE.
5. IF compilation fails, THE LocalSubprocessJudgeRunner SHALL assign verdict CE and store the compiler output truncated to 4 KB.
6. WHEN the Submission output matches the expected output (exact match after stripping trailing whitespace per line), THE runner SHALL assign verdict AC for that testcase.
7. WHEN the Submission output does not match the expected output, THE runner SHALL assign verdict WA for that testcase.
8. WHEN a runtime exception or non-zero exit code occurs, THE runner SHALL assign verdict RE for that testcase.
9. WHEN all testcases for a Submission are judged, THE runner SHALL compute the final verdict using the priority order TLE > RE > WA > AC and update the Submission record in SQLite.
10. THE LocalSubprocessJudgeRunner SHALL run in the same process as the API server in the MVP (synchronous or via a background thread); a separate worker process is a Production Hardening upgrade.

---

### Requirement 7: Submission History and Results

**User Story:** As a Student, I want to view my submission history and detailed results, so that I can understand my mistakes and improve my solutions.

#### Acceptance Criteria

1. THE System SHALL display a paginated list (25 submissions per page) of all Submissions made by the authenticated Student, ordered by submission time descending.
2. WHEN a Student opens a Submission detail page, THE System SHALL display the verdict, language, submission time, compile error message if applicable, and per-testcase results for testcases not marked as hidden.
3. WHILE a Submission has status PD, THE System SHALL update the Submission status on the Student's browser within 5 seconds of the runner completing the verdict (via polling or page refresh).
4. IF a Submission has verdict CE, THE System SHALL display the full compiler error output to the submitting Student.
5. THE System SHALL hide the stdin input, stdout output, and expected output of testcases marked as hidden from Students.

---

### Requirement 8: Teacher and Admin Dashboard

**User Story:** As a Teacher or Admin, I want a dashboard to manage problems, users, and submissions, so that I can operate the platform without direct database access.

#### Acceptance Criteria

1. IF a User without the Teacher, Admin, or Super_Admin role attempts to access the Teacher/Admin dashboard, THE System SHALL return an HTTP 403 response.
2. THE System SHALL allow a Teacher to create, edit, and delete Problems from the dashboard.
3. THE System SHALL allow a Teacher to upload problem statement files and testcase ZIPs from the dashboard.
4. THE System SHALL allow an Admin to create User accounts and assign any Role except Super_Admin.
5. THE System SHALL allow an Admin to view all Submissions across all Users and Problems, paginated at 50 per page ordered by submission time descending.
6. THE System SHALL allow a Teacher to view all Submissions for their Problems.

---

### Requirement 9: Seed Data and Local Setup

**User Story:** As a Developer, I want the system to come with seed data and a simple setup script, so that I can start the MVP with a single command.

#### Acceptance Criteria

1. THE System SHALL provide a setup script (`python -m app.db.init_db`) that creates the SQLite database, runs all migrations, and inserts seed users.
2. THE seed data SHALL include exactly 4 users: one Super_Admin, one Admin, one Teacher, and one Student, each with a known default password documented in the README.
3. WHEN the setup script is run on a machine with Python 3.12+ and the required pip packages installed, THE System SHALL be ready to serve requests at `http://localhost:8000` without any additional configuration.
4. THE System SHALL NOT require Docker, PostgreSQL, or Redis to run the MVP.

---

### Requirement 10: Production Hardening (Future Upgrade Path)

**User Story:** As an Admin, I want a documented upgrade path to production-grade infrastructure, so that the platform can scale beyond a single developer machine.

#### Acceptance Criteria

1. THE System SHALL document the upgrade path from SQLite to PostgreSQL in `docs/decision-log.md`.
2. THE System SHALL document the upgrade path from in-memory rate limiting to Redis-based rate limiting.
3. THE System SHALL document the upgrade path from `LocalSubprocessJudgeRunner` to `DockerSandboxJudgeRunner` with full sandbox isolation.
4. THE System SHALL document the upgrade path from synchronous in-process judging to an async Redis-backed job queue.
5. THE System SHALL document the Docker Compose configuration needed to run the full production stack.
6. THE `DockerSandboxJudgeRunner` (when implemented) SHALL enforce: no network access, read-only testcase mounts, CPU time limit, wall time limit (CPU + 2s), memory limit, output size limit (64 MB), and maximum process count of 1.
