"""create_initial_tables

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

Creates the four core tables for the MindX Online Judge MVP:
  - users
  - problems
  - submissions
  - password_reset_tokens
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ users
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(128), nullable=False),
        sa.Column(
            "role",
            sa.Enum("student", "teacher", "admin", "super_admin", name="userrole"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # --------------------------------------------------------------- problems
    op.create_table(
        "problems",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("statement_md", sa.Text(), nullable=True),
        sa.Column("time_limit_ms", sa.Integer(), nullable=False),
        sa.Column("memory_limit_mb", sa.Integer(), nullable=False),
        sa.Column("allowed_languages", sa.Text(), nullable=True),
        sa.Column("scoring_mode", sa.String(50), nullable=False),
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("package_path", sa.String(500), nullable=True),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("code", name="uq_problems_code"),
    )
    op.create_index("ix_problems_code", "problems", ["code"], unique=True)

    # ------------------------------------------------------------- submissions
    op.create_table(
        "submissions",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("problem_id", sa.String(36), sa.ForeignKey("problems.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("language", sa.String(20), nullable=False),
        sa.Column("source_path", sa.String(500), nullable=True),
        sa.Column("verdict", sa.String(10), nullable=False, server_default="PD"),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("compile_error", sa.Text(), nullable=True),
        sa.Column("testcase_results", sa.Text(), nullable=True),
        sa.Column("judged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ------------------------------------------------- password_reset_tokens
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token", sa.String(64), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("token", name="uq_password_reset_tokens_token"),
    )
    op.create_index(
        "ix_password_reset_tokens_token",
        "password_reset_tokens",
        ["token"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_password_reset_tokens_token", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_table("submissions")
    op.drop_index("ix_problems_code", table_name="problems")
    op.drop_table("problems")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    # Drop the enum type (needed for PostgreSQL; no-op for SQLite)
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)
