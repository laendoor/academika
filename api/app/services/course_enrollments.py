import uuid

from app.db.query_builder import QueryBuilder
from app.models.course_enrollment import CourseEnrollment
from app.schemas.course_enrollments import CourseEnrollmentCreate, CourseEnrollmentUpdate
from app.services.base import BaseService


class CourseEnrollmentService(BaseService[CourseEnrollment, CourseEnrollmentCreate, CourseEnrollmentUpdate]):
    model = CourseEnrollment

    async def list_filtered(
        self,
        skip: int = 0,
        limit: int = 20,
        student_id: uuid.UUID | None = None,
        course_id: uuid.UUID | None = None,
        year: int | None = None,
        term: str | None = None,
    ) -> tuple[int, list[CourseEnrollment]]:
        builder = QueryBuilder(CourseEnrollment)
        if student_id is not None:
            builder.filter(CourseEnrollment.student_id == student_id)
        if course_id is not None:
            builder.filter(CourseEnrollment.course_id == course_id)
        if year is not None:
            builder.filter(CourseEnrollment.year == year)
        if term is not None:
            builder.filter(CourseEnrollment.term == term)
        total = await self.session.scalar(builder.count_stmt())
        result = await self.session.execute(builder.paginated(skip, limit))
        return total or 0, list(result.scalars().all())
