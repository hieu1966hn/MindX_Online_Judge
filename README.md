# MindX Online Judge Workspace

> Internal web-based coding judge for MindX, inspired by LQDOJ/DMOJ, but designed to be owned and operated independently by MindX.

## 0. Purpose

Build a private MindX Online Judge system where:

- Teachers/Admins can upload programming problems from DOC/DOCX/PDF/Markdown.
- A multi-question exam file can be split into separate problems.
- Teachers/Admins can upload testcase packages following a clear rule.
- Students can code directly in the website or upload source files.
- The system compiles/runs submissions in a sandbox and returns results immediately.
- Results include AC, WA, TLE, MLE, RE, CE, score, passed tests, failed tests, and submission logs.
- The final product is a real website similar in purpose to LQDOJ, with Problems, Contests, Courses/Classes, Groups, Rankings, Submissions, and Admin Dashboard.
- AI Agent support is available at the project folder level to help import problems, normalize statements, validate testcase packages, and generate teacher-facing materials.

This README is written for an implementation Agent. Follow it as the main product and engineering plan.

---

## 1. Reference Systems

### 1.1 LQDOJ Website

Reference URL:

```text
https://lqdoj.edu.vn/
```

Observed product pattern:

- Home/news feed.
- Problems.
- Contests.
- Courses.
- Groups.
- Login/signup.
- Ongoing contests.
- Top Rating.
- Top Score.
- Top Contributors.
- Powered by DMOJ.

### 1.2 LQDOJ Source Code

Reference repo:

```text
https://github.com/LQDJudge/online-judge.git
```

Observed technical/product features from the repo README:

- Based on DMOJ.
- Supports many languages including C, C++, Java, Pascal, Python, PyPy.
- Contest management.
- User rating and performance tracking.
- Plagiarism detection via Stanford MOSS.
- Real-time chat.
- Multi-language support.
- Dark/light theme.
- Organization management.
- Uses site, judge bridge, judge server, Redis, MariaDB/MySQL, WebSocket, Celery, and separate judge process.

### 1.3 Important License Note

The referenced LQDOJ repository uses AGPL-3.0. Do not blindly copy or deeply modify the codebase for a closed internal product without legal review.

Recommended approach:

1. Use LQDOJ/DMOJ as an architectural and UX reference.
2. Build a MindX-owned implementation for the MVP.
3. If forking LQDOJ/DMOJ is considered, document license obligations before production use.

---

## 2. Product Vision

Product name placeholder:

```text
MindX Judge Workspace
```

One-line description:

```text
A private MindX web platform for coding practice, exams, automatic judging, testcase management, class/contest operation, and AI-assisted problem import.
```

Target users:

- Student.
- Teacher.
- Content/R&D team.
- Center/Admin manager.
- Super Admin.
- AI Agent operating inside the project folder.

---

## 3. Core User Flows

### 3.1 Student Flow

1. Student logs in.
2. Student enters class/course/contest/problem list.
3. Student opens a problem statement.
4. Student writes code in browser editor or uploads a file.
5. Student selects language.
6. Student submits.
7. System returns result immediately.
8. Student reviews score, verdict, compile error/runtime error details, and visible testcase feedback.
9. Student resubmits until accepted or until contest/exam rule blocks resubmission.

### 3.2 Teacher/Admin Flow

1. Teacher logs in.
2. Teacher creates a course/class/contest/exam.
3. Teacher uploads problem statement manually or imports DOC/PDF.
4. Teacher splits an exam file into Problem A, B, C, etc.
5. Teacher uploads testcase zip.
6. System validates testcase format.
7. Teacher adds time limit, memory limit, scoring method, tags, allowed languages, and sample tests.
8. Teacher optionally uploads official solution for benchmark.
9. Teacher publishes the problem/contest to selected classes/groups.
10. Teacher monitors submissions, scoreboard, plagiarism flags, and class performance.

### 3.3 AI Agent Flow

The Agent works inside the project folder and can:

1. Read uploaded DOC/PDF/Markdown problem files.
2. Extract title, statement, input format, output format, constraints, samples, subtasks, and notes.
3. Split one exam file into multiple problems.
4. Convert each problem to `statement.md`.
5. Create or update `problem.yaml`.
6. Validate testcase zip structure.
7. Run official solution against testcase set.
8. Generate missing teacher notes or warning checklist.
9. Create import-ready problem package.
10. Never run untrusted student code outside the judge sandbox.

---

## 4. MVP Scope

The MVP must prioritize a working internal judge before advanced community features.

### 4.1 Must Have

- Web login.
- Role-based access: Student, Teacher, Admin, Super Admin.
- Problem list.
- Problem detail page.
- Online code editor.
- Source file upload.
- Submit button.
- Submission history.
- Automatic judge for Python 3 and C++17/C++20.
- Testcase zip upload.
- Testcase validation.
- Time limit and memory limit.
- Verdicts: AC, WA, TLE, MLE, RE, CE, Pending, Judging.
- Score per problem.
- Contest/exam creation.
- Basic scoreboard.
- Admin problem management.
- AI-assisted DOC/PDF import to Markdown/problem package.

### 4.2 Should Have

- Class/course grouping.
- Problem tags and difficulty.
- Subtask scoring.
- Sample tests shown to students.
- Hidden tests hidden from students.
- Rejudge submissions.
- Export results to CSV/XLSX.
- Basic plagiarism check.
- Dark/light theme.
- Vietnamese/English UI-ready structure.

### 4.3 Could Have Later

- Rating system.
- Public/community problem proposal.
- Real-time chat.
- Full MOSS integration.
- Organization/center hierarchy.
- Advanced analytics dashboard.
- AI explanation for teacher only.
- AI-assisted solution review.
- LTI/LMS integration.

### 4.4 Out of MVP

- Full clone of LQDOJ.
- Public community platform.
- Large-scale rating ecosystem.
- Native mobile app.
- Complex interactive problems.
- Distributed multi-region judging.

---

## 5. Recommended Architecture

### 5.1 High-Level Components

```text
mindx-judge-workspace/
  web-app/              # Student/teacher/admin website
  api-server/           # REST/GraphQL API
  judge-worker/         # Sandbox runner and verdict engine
  ai-agent-tools/       # Import, split, validate, benchmark tools
  problem-packages/     # Local problem package workspace
  storage/              # Local dev storage mount
  docs/                 # Product and technical documents
  infra/                # Docker Compose, deployment configs
```

### 5.2 Suggested Tech Stack

Use this unless the existing Agent/project constraints require otherwise.

Frontend:

- Next.js or React.
- TypeScript.
- Tailwind CSS.
- Monaco Editor for coding workspace.

Backend:

- FastAPI, Django, or NestJS.
- PostgreSQL for main database.
- Redis for queue/status/cache.
- Object storage: local filesystem for MVP, MinIO/S3-compatible later.

Judge:

- Docker-based sandbox for MVP.
- Separate worker process.
- Queue-based judging.
- Language runners for Python 3 and C++17/C++20 first.
- Strict CPU, memory, process, network, and filesystem limits.

AI Agent tools:

- Python scripts for document parsing and package validation.
- DOCX parser.
- PDF parser.
- Markdown normalizer.
- Testcase validator.
- Official solution benchmark runner.

Deployment:

- Docker Compose for local/internal MVP.
- Later: Kubernetes or VM deployment if scale requires.

---

## 6. Data Model Draft

Minimum database entities:

```text
User
  id
  name
  email
  password_hash / SSO identity
  role
  created_at
  updated_at

Course
  id
  title
  description
  teacher_id
  visibility
  created_at

ClassGroup
  id
  name
  course_id
  center_name
  teacher_id

Enrollment
  id
  user_id
  class_group_id
  role_in_class

Problem
  id
  code
  title
  statement_markdown
  difficulty
  tags
  time_limit_ms
  memory_limit_mb
  allowed_languages
  scoring_mode
  visibility
  created_by
  created_at
  updated_at

TestcaseSet
  id
  problem_id
  version
  storage_path
  checksum
  is_active
  created_by
  created_at

Testcase
  id
  testcase_set_id
  name
  input_path
  output_path
  score
  is_sample
  is_hidden
  group_name

Contest
  id
  title
  description
  start_time
  end_time
  duration_minutes
  format
  visibility
  created_by

ContestProblem
  id
  contest_id
  problem_id
  alias
  points
  order_index

Submission
  id
  user_id
  problem_id
  contest_id
  language
  source_path
  source_text_snapshot
  status
  verdict
  score
  max_score
  runtime_ms
  memory_kb
  created_at
  judged_at

SubmissionTestResult
  id
  submission_id
  testcase_id
  verdict
  runtime_ms
  memory_kb
  stdout_path
  stderr_path
  message
```

---

## 7. Problem Package Standard

All imported/generated problems should follow this structure:

```text
problem_packages/
  <problem_code>/
    problem.yaml
    statement.md
    assets/
      images/
    tests/
      samples/
        01.in
        01.out
        02.in
        02.out
      hidden/
        01.in
        01.out
        02.in
        02.out
      subtasks/
        subtask_1/
          01.in
          01.out
        subtask_2/
          01.in
          01.out
    solutions/
      official.cpp
      official.py
    notes/
      teacher_note.md
      ai_import_report.md
```

### 7.1 `problem.yaml` Example

```yaml
code: sum_two_numbers
title: Tổng hai số
difficulty: easy
tags:
  - input-output
  - arithmetic
time_limit_ms: 1000
memory_limit_mb: 256
allowed_languages:
  - python3
  - cpp17
  - cpp20
scoring_mode: all_or_nothing
samples:
  - input: tests/samples/01.in
    output: tests/samples/01.out
testcases:
  hidden_dir: tests/hidden
checker: standard_diff
created_by: ai_importer
```

### 7.2 Testcase Upload Zip Rule

Accepted zip format:

```text
<problem_code>.zip
  problem.yaml
  statement.md
  tests/
    samples/
      01.in
      01.out
    hidden/
      01.in
      01.out
      02.in
      02.out
```

Validation rules:

- Every `.in` file must have matching `.out` file.
- Testcase names must be deterministic: `01.in`, `01.out`, `02.in`, `02.out`.
- No executable files allowed inside testcase zip.
- No nested zip files.
- No absolute paths.
- No `../` path traversal.
- Max zip size must be configured.
- Max individual testcase input size must be configured.
- Hidden testcase outputs must never be exposed to students.

---

## 8. Judge Design

### 8.1 Submission Lifecycle

```text
Student submits
  -> API stores submission
  -> API pushes judge job to queue
  -> Judge worker pulls job
  -> Judge worker prepares sandbox
  -> Compile if needed
  -> Run against sample/hidden tests
  -> Compare output
  -> Store per-test result
  -> Update submission verdict and score
  -> Web UI polls or receives live update
```

### 8.2 Verdict Rules

```text
AC   Accepted
WA   Wrong Answer
TLE  Time Limit Exceeded
MLE  Memory Limit Exceeded
RE   Runtime Error
CE   Compilation Error
OLE  Output Limit Exceeded
IE   Internal Error
PD   Pending
JG   Judging
```

### 8.3 Language Runner MVP

Python 3:

```text
compile: none
run: python3 main.py
```

C++17:

```text
compile: g++ -std=c++17 -O2 -pipe -static -s main.cpp -o main
run: ./main
```

C++20:

```text
compile: g++ -std=c++20 -O2 -pipe -static -s main.cpp -o main
run: ./main
```

Note: If static linking causes issues in the target environment, remove `-static` and document the reason.

### 8.4 Sandbox Requirements

Never run student code directly on the host machine.

Minimum sandbox restrictions:

- No network.
- Read-only problem/testcase input mount.
- Isolated temp working directory.
- CPU time limit.
- Wall time limit.
- Memory limit.
- Output size limit.
- Process count limit.
- No access to host secrets.
- No Docker socket mounted inside runner.
- Cleanup after every run.

---

## 9. Web UI Pages

### 9.1 Public/Auth Pages

- `/login`
- `/signup` or admin-created account only
- `/forgot-password`

### 9.2 Student Pages

- `/` home/news/dashboard
- `/problems`
- `/problems/:code`
- `/problems/:code/submit`
- `/submissions`
- `/submissions/:id`
- `/contests`
- `/contests/:id`
- `/contests/:id/scoreboard`
- `/courses`
- `/courses/:id`
- `/groups/:id`

### 9.3 Teacher/Admin Pages

- `/admin`
- `/admin/problems`
- `/admin/problems/new`
- `/admin/problems/:id/edit`
- `/admin/problems/:id/testcases`
- `/admin/import`
- `/admin/contests`
- `/admin/courses`
- `/admin/classes`
- `/admin/users`
- `/admin/submissions`
- `/admin/rejudge`
- `/admin/reports`

---

## 10. AI Agent Import Pipeline

### 10.1 Input Types

- `.doc`
- `.docx`
- `.pdf`
- `.md`
- `.txt`
- Images later if OCR is explicitly needed

### 10.2 Pipeline

```text
Upload file
  -> Extract raw text
  -> Detect problem boundaries
  -> Split into problems
  -> Extract title/statement/input/output/constraints/samples
  -> Normalize to Markdown
  -> Generate problem.yaml draft
  -> Validate missing fields
  -> Create problem package folder
  -> Ask teacher/admin to review before publish
```

### 10.3 AI Import Report

For every imported problem, create:

```text
notes/ai_import_report.md
```

Report must include:

- Source file name.
- Detected problem title.
- Confidence level.
- Missing information.
- Extracted samples.
- Suggested tags.
- Suggested time/memory limits.
- Warnings for ambiguous constraints.

### 10.4 Human Approval Rule

AI may prepare problem packages, but publishing to students requires Teacher/Admin approval.

---

## 11. Implementation Phases

## Phase 0 - Repository Setup and Decision Log

Goal: prepare the project skeleton and document decisions.

Tasks:

- Create monorepo folder structure.
- Create `docs/architecture.md`.
- Create `docs/decision-log.md`.
- Create `.env.example`.
- Create Docker Compose for database, redis, api, web, worker.
- Decide whether backend uses FastAPI, Django, or NestJS.
- Decide whether frontend uses Next.js or plain React.

Definition of Done:

- Developer can run the empty app locally.
- README, env example, and architecture draft exist.

---

## Phase 1 - Basic Web and Auth

Goal: allow users to log in and access role-based pages.

Tasks:

- Implement user model.
- Implement login/logout.
- Implement roles: Student, Teacher, Admin, Super Admin.
- Implement basic dashboard.
- Implement protected routes.
- Implement seed users for local dev.

Definition of Done:

- Student can access student dashboard.
- Teacher can access teacher dashboard.
- Admin can access admin dashboard.
- Unauthorized users are blocked.

---

## Phase 2 - Problem Management

Goal: create and view problems.

Tasks:

- Create problem CRUD.
- Add Markdown statement rendering.
- Add tags, difficulty, time limit, memory limit.
- Add allowed languages.
- Add sample tests display.
- Add problem list/search/filter.

Definition of Done:

- Teacher can create a problem.
- Student can open problem detail.
- Markdown renders correctly.
- Sample tests are visible.

---

## Phase 3 - Testcase Package Upload

Goal: upload and validate testcase zips.

Tasks:

- Implement testcase zip upload.
- Validate folder structure.
- Validate `.in`/`.out` pairs.
- Store testcase package version.
- Activate/deactivate testcase set.
- Prevent path traversal and executable files.

Definition of Done:

- Valid testcase zip is accepted.
- Invalid testcase zip returns clear errors.
- Active testcase set is linked to a problem.

---

## Phase 4 - Submission UI

Goal: students can submit code.

Tasks:

- Add Monaco Editor.
- Add language selector.
- Add file upload for `.py`, `.cpp`, `.java` later.
- Store source snapshot.
- Create submission record.
- Show submission history.

Definition of Done:

- Student can submit Python 3 code.
- Student can submit C++17/C++20 code.
- Submission appears as Pending/Judging before result.

---

## Phase 5 - Judge Worker MVP

Goal: judge Python and C++ submissions safely.

Tasks:

- Create judge job queue.
- Create worker service.
- Implement Python runner.
- Implement C++ compile and run.
- Implement standard diff checker.
- Implement time limit.
- Implement memory limit.
- Implement output limit.
- Store per-test results.
- Return final verdict and score.

Definition of Done:

- Correct code gets AC.
- Wrong code gets WA.
- Infinite loop gets TLE.
- Compilation error gets CE.
- Runtime error gets RE.
- Student sees result on the web.

---

## Phase 6 - Contest and Scoreboard

Goal: run basic internal contests/exams.

Tasks:

- Create contest CRUD.
- Add start/end time.
- Add duration/window rule.
- Add contest problem aliases A/B/C.
- Add contest registration or class assignment.
- Add scoreboard.
- Add freeze option later.

Definition of Done:

- Teacher can create contest with problems.
- Student can join allowed contest.
- Submissions count toward contest score.
- Scoreboard updates.

---

## Phase 7 - Course/Class/Group

Goal: organize MindX internal teaching use cases.

Tasks:

- Create course/class/group models.
- Assign teachers.
- Enroll students.
- Assign problem sets or contests to classes.
- Filter dashboard by class/course.
- Export class result report.

Definition of Done:

- Teacher can see only assigned classes.
- Student can see assigned work.
- Admin can export class results.

---

## Phase 8 - AI-Assisted Problem Import

Goal: convert DOC/PDF exams into problem packages.

Tasks:

- Create upload page for source files.
- Extract text from DOCX/PDF.
- Split multi-question file into problems.
- Generate `statement.md`.
- Generate `problem.yaml` draft.
- Generate `ai_import_report.md`.
- Allow teacher review and edit before publishing.

Definition of Done:

- Teacher uploads one exam PDF/DOCX.
- System generates multiple draft problems.
- Teacher can review, edit, and publish.

---

## Phase 9 - Reporting and Operations

Goal: make the system usable for real classes.

Tasks:

- Submission analytics.
- Student progress dashboard.
- CSV/XLSX export.
- Rejudge problem or contest.
- Audit logs.
- Admin system status page.
- Backup/restore strategy.

Definition of Done:

- Teacher can export results.
- Admin can inspect judge status.
- Admin can rejudge after testcase update.

---

## 12. Local Development Commands

The exact commands depend on final stack. Keep these placeholders updated.

```bash
# Start local services
cd infra
docker compose up -d

# Start backend
cd ../api-server
# install dependencies here
# run migration here
# run server here

# Start frontend
cd ../web-app
# install dependencies here
# run dev server here

# Start judge worker
cd ../judge-worker
# run worker here
```

---

## 13. Security Checklist

Before any internal pilot:

- Student code must run only in sandbox.
- Judge worker must not mount secrets.
- Judge worker must not expose network.
- Submission source must be stored safely.
- Hidden testcase output must never be leaked.
- Admin routes must require proper roles.
- File uploads must be size-limited and type-validated.
- Zip extraction must block path traversal.
- Rate-limit submissions.
- Log judge errors without leaking infrastructure secrets.
- Backup database and testcase storage.

---

## 14. MindX Branding and UX Direction

The final product should feel like a MindX internal product, not a generic clone.

UI direction:

- Clean dashboard.
- Strong education/product feel.
- Simple student flow: Read -> Code -> Submit -> See result.
- Teacher flow should be clear: Create problem -> Upload testcase -> Publish -> Track.
- Use MindX brand colors and visual identity when available.
- Prioritize Vietnamese UI first, English-ready later.

Main navigation recommendation:

```text
Home
Problems
Contests
Courses
Groups
Submissions
Rankings
Admin
```

---

## 15. Agent Operating Rules

When implementing this project, the Agent must:

1. Work incrementally by phase.
2. Keep code runnable after each phase.
3. Prefer a working MVP over a full LQDOJ clone.
4. Do not execute untrusted submissions on the host machine.
5. Keep database schema migrations versioned.
6. Keep problem package format stable and documented.
7. Create tests for validator and judge worker.
8. Create seed data for demo problems.
9. Keep UI simple and usable before adding advanced features.
10. Document any major architecture decision in `docs/decision-log.md`.
11. Flag any AGPL/forking/legal issue before using LQDOJ code directly.
12. Ask for human approval before publishing AI-imported problems.

---

## 16. First Sprint Recommendation

Sprint goal:

```text
A student can log in, open one sample problem, submit Python/C++ code, and receive AC/WA/TLE/CE/RE from hidden tests.
```

Sprint tasks:

- Set up repo structure.
- Create frontend shell.
- Create backend API shell.
- Create database schema for User, Problem, TestcaseSet, Submission.
- Seed one sample problem: sum two numbers.
- Upload or seed testcase package.
- Implement submission API.
- Implement judge worker for Python and C++.
- Implement submission result page.

Sprint demo script:

1. Login as student.
2. Open problem `sum_two_numbers`.
3. Submit correct Python solution -> AC.
4. Submit wrong Python solution -> WA.
5. Submit infinite loop -> TLE.
6. Submit invalid C++ syntax -> CE.
7. Login as teacher.
8. View submissions and class result.

---

## 17. Success Criteria

MVP is successful when:

- Teachers can create problems and upload testcases without engineering help.
- Students can code in the browser or upload code files.
- Judge returns reliable results within seconds for normal submissions.
- Admin can run contests/exams internally.
- AI Agent can convert DOC/PDF into draft problem packages.
- MindX can operate the system independently without relying on external OJ platforms.

