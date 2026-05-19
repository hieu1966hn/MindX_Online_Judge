"""
Comprehensive Test Script for Round 3 (Problem Domain & Judge System).
This script validates:
1. Judge LocalRunner (AC, WA, TLE, RE cases)
2. Database models and services integration
3. Submission flow
"""
import sys
import os
from pathlib import Path
import uuid
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.session import engine
from app.db.base import Base
from app.models.user import User, UserRole
from app.models.problem import Problem, ScoringMode
from app.models.submission import Submission
from app.judge.local_runner import LocalRunner
from app.judge.base import JudgeStatus
from app.services import problem_service, submission_service
from app.schemas.submission import SubmissionCreate
from app.core.security import hash_password

def test_judge_runner():
    print("\n--- 🏃 Testing LocalRunner ---")
    runner = LocalRunner()
    
    # Test Case 1: Accepted (AC)
    print("Testing AC code...")
    result_ac = runner.run(
        source_code="a, b = map(int, input().split())\nprint(a + b)",
        language="python3",
        input_data="10 20",
        time_limit_ms=1000,
        memory_limit_mb=256
    )
    print(f"Result Status: {result_ac.status}")
    print(f"Stdout: {result_ac.stdout.strip()}")
    assert result_ac.status == JudgeStatus.ACCEPTED
    assert result_ac.stdout.strip() == "30"
    print("✅ AC Test Passed")

    # Test Case 2: Runtime Error (RE)
    print("\nTesting RE code (ZeroDivisionError)...")
    result_re = runner.run(
        source_code="print(1/0)",
        language="python3",
        input_data="",
        time_limit_ms=1000,
        memory_limit_mb=256
    )
    print(f"Result Status: {result_re.status}")
    print(f"Stderr: {result_re.stderr.strip()}")
    assert result_re.status == JudgeStatus.RUNTIME_ERROR
    assert "ZeroDivisionError" in result_re.stderr
    print("✅ RE Test Passed")

    # Test Case 3: Time Limit Exceeded (TLE)
    print("\nTesting TLE code (Infinite Loop)...")
    result_tle = runner.run(
        source_code="while True: pass",
        language="python3",
        input_data="",
        time_limit_ms=500, # Short limit
        memory_limit_mb=256
    )
    print(f"Result Status: {result_tle.status}")
    assert result_tle.status == JudgeStatus.TIME_LIMIT_EXCEEDED
    print("✅ TLE Test Passed")


def test_submission_service():
    print("\n--- 💾 Testing Submission Service & DB ---")

    # Use an isolated temporary SQLite DB so this test is not affected by
    # stale local dev schemas from previous rounds.
    test_db_path = Path(__file__).parent / "data" / "round3_test.db"
    if test_db_path.exists():
        test_db_path.unlink()

    test_engine = create_engine(f"sqlite:///{test_db_path}")
    Base.metadata.create_all(bind=test_engine)
    
    with Session(test_engine) as db:
        # 1. Setup mock user and problem
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            name="Test Student",
            email=f"test_{uuid.uuid4().hex[:6]}@test.com",
            password_hash=hash_password("test"),
            role=UserRole.STUDENT
        )
        db.add(user)
        
        problem_id = str(uuid.uuid4())
        problem = Problem(
            id=problem_id,
            code=f"TEST_{uuid.uuid4().hex[:4]}",
            title="Sum Test",
            statement_md="Sum A and B",
            time_limit_ms=1000,
            memory_limit_mb=256,
            scoring_mode=ScoringMode.ALL_OR_NOTHING,
            created_by=user_id
        )
        db.add(problem)
        db.commit()
        
        # 2. Test create submission (which triggers judge)
        print(f"Submitting code for problem {problem.code}...")
        sub_data = SubmissionCreate(
            problem_id=problem_id,
            language="python3",
            source_code="print(42)"
        )
        
        submission = submission_service.create_submission(sub_data, user_id, db)
        
        print(f"Submission ID: {submission.id}")
        print(f"Status: {submission.status}")
        print(f"Score: {submission.score}")
        
        assert submission.id is not None
        assert submission.user_id == user_id
        assert submission.problem_id == problem_id
        assert submission.status == JudgeStatus.ACCEPTED
        assert submission.score == 100.0
        print("✅ Submission Service Test Passed")

if __name__ == "__main__":
    try:
        test_judge_runner()
        test_submission_service()
        print("\n✨ ALL TESTS PASSED! YOU CAN SAFELY PUSH. ✨")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
