"""
Database initialization script for MindX Online Judge.

Creates tables and seeds initial data:
- 1 super_admin user (admin@mindx.edu.vn / Admin@123)
- 1 teacher user (teacher@mindx.edu.vn / Teacher@123)
- 2 student users (student1@mindx.edu.vn / Student@123, student2@mindx.edu.vn / Student@123)
- 2 sample problems (Sum Two Numbers, Fibonacci)

Run this script once to initialize the database:
    python -m app.db.init_db
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import Base
from app.db.session import engine
from app.models.user import User, UserRole
from app.models.problem import Problem
from app.models.submission import Submission
from app.core.security import hash_password
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone


def init_database():
    """Create all tables and seed initial data."""
    print("🔧 Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    # Seed data
    with Session(engine) as session:
        # Check if data already exists
        existing_users = session.query(User).count()
        if existing_users > 0:
            print(f"⚠️  Database already contains {existing_users} users. Skipping seed.")
            return
        
        print("📝 Seeding initial data...")
        
        # Create users
        users = [
            User(
                id=str(uuid.uuid4()),
                name="Admin User",
                email="admin@mindx.edu.vn",
                password_hash=hash_password("Admin@123"),
                role=UserRole.SUPER_ADMIN,
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ),
            User(
                id=str(uuid.uuid4()),
                name="Teacher Nguyen",
                email="teacher@mindx.edu.vn",
                password_hash=hash_password("Teacher@123"),
                role=UserRole.TEACHER,
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ),
            User(
                id=str(uuid.uuid4()),
                name="Student One",
                email="student1@mindx.edu.vn",
                password_hash=hash_password("Student@123"),
                role=UserRole.STUDENT,
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ),
            User(
                id=str(uuid.uuid4()),
                name="Student Two",
                email="student2@mindx.edu.vn",
                password_hash=hash_password("Student@123"),
                role=UserRole.STUDENT,
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ),
        ]
        
        for user in users:
            session.add(user)
        
        # Create sample problems
        problems = [
            Problem(
                id=str(uuid.uuid4()),
                code="SUM2",
                title="Sum Two Numbers",
                statement_md="Given two integers A and B, return their sum.",
                time_limit_ms=1000,
                memory_limit_mb=256,
                package_path="packages/SUM2",
                created_by=users[1].id,  # teacher
                created_at=datetime.now(timezone.utc),
            ),
            Problem(
                id=str(uuid.uuid4()),
                code="FIB",
                title="Fibonacci Number",
                statement_md="Calculate the N-th Fibonacci number.",
                time_limit_ms=2000,
                memory_limit_mb=256,
                package_path="packages/FIB",
                created_by=users[1].id,  # teacher
                created_at=datetime.now(timezone.utc),
            ),
        ]
        
        for problem in problems:
            session.add(problem)
        
        session.commit()
        print("✓ Seeded 4 users and 2 problems")
    
    print("\n✅ Database initialization complete!")
    print("\n📋 Test Accounts:")
    print("   Admin:    admin@mindx.edu.vn / Admin@123")
    print("   Teacher:  teacher@mindx.edu.vn / Teacher@123")
    print("   Student1: student1@mindx.edu.vn / Student@123")
    print("   Student2: student2@mindx.edu.vn / Student@123")


if __name__ == "__main__":
    init_database()
