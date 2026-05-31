"""rename_tables_to_plural

Revision ID: e22a6112a67a
Revises: a58bc63f42f6
Create Date: 2026-05-30 21:05:26.506269

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e22a6112a67a"
down_revision: str | Sequence[str] | None = "a58bc63f42f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.rename_table("degree", "degrees")
    op.rename_table("course", "courses")
    op.rename_table("study_plan", "study_plans")
    op.rename_table("study_plan_course", "study_plans_courses")
    op.rename_table("student", "students")
    op.rename_table("course_enrollment", "course_enrollments")
    op.rename_table("course_prerequisite", "course_prerequisites")
    op.rename_table("lkp_enrollment_type", "lkp_enrollment_types")


def downgrade() -> None:
    op.rename_table("degrees", "degree")
    op.rename_table("courses", "course")
    op.rename_table("study_plans", "study_plan")
    op.rename_table("study_plans_courses", "study_plan_course")
    op.rename_table("students", "student")
    op.rename_table("course_enrollments", "course_enrollment")
    op.rename_table("course_prerequisites", "course_prerequisite")
    op.rename_table("lkp_enrollment_types", "lkp_enrollment_type")
