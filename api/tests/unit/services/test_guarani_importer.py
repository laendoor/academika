from unittest.mock import AsyncMock, patch

import pytest

from app.services.guarani_importer import GuaraniImporterService
from tests.unit.factories import (
    make_course,
    make_course_row,
    make_degree,
    make_degree_row,
    make_enrollment_history_row,
    make_enrollment_row,
    make_prerequisite_row,
    make_student,
    make_student_row,
    make_study_plan,
    make_study_plan_course_row,
)


@pytest.mark.asyncio
class TestUpsertStudents:
    async def test_skips_when_degree_not_found(self):
        service = GuaraniImporterService(AsyncMock())

        with patch.object(service, "_fetch_degrees", return_value={}):
            with patch.object(service, "_fetch_study_plans", return_value={}):
                upserted, skipped = await service._upsert_students([make_student_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_upserts_when_degree_found(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        degree = make_degree("P")

        with patch.object(service, "_fetch_degrees", return_value={"P": degree}):
            with patch.object(service, "_fetch_study_plans", return_value={}):
                upserted, skipped = await service._upsert_students([make_student_row(degree_code="P")])

        assert upserted == 1
        assert skipped == 0
        session.execute.assert_called_once()

    async def test_commits_at_end(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        degree = make_degree("P")

        with patch.object(service, "_fetch_degrees", return_value={"P": degree}):
            with patch.object(service, "_fetch_study_plans", return_value={}):
                await service._upsert_students([make_student_row()])

        session.commit.assert_called_once()

    async def test_mixed_rows_correct_counts(self):
        service = GuaraniImporterService(AsyncMock())
        degree = make_degree("P")

        rows = [
            make_student_row(doc_id="111", degree_code="P"),
            make_student_row(doc_id="222", degree_code="X"),  # missing degree
            make_student_row(doc_id="333", degree_code="P"),
        ]

        with patch.object(service, "_fetch_degrees", return_value={"P": degree}):
            with patch.object(service, "_fetch_study_plans", return_value={}):
                upserted, skipped = await service._upsert_students(rows)

        assert upserted == 2
        assert skipped == 1

    async def test_plan_id_none_when_study_plan_not_found(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        degree = make_degree("P")

        with patch.object(service, "_fetch_degrees", return_value={"P": degree}):
            with patch.object(service, "_fetch_study_plans", return_value={}):
                upserted, skipped = await service._upsert_students([make_student_row(plan_year=9999)])

        assert upserted == 1
        call_args = session.execute.call_args[0][0]
        assert call_args.compile().params.get("plan_id") is None

    async def test_plan_id_set_when_study_plan_found(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        degree = make_degree("P")
        plan = make_study_plan(degree.id, year=2015)

        with patch.object(service, "_fetch_degrees", return_value={"P": degree}):
            with patch.object(service, "_fetch_study_plans", return_value={(degree.id, 2015): plan}):
                await service._upsert_students([make_student_row(plan_year=2015)])

        call_args = session.execute.call_args[0][0]
        assert call_args.compile().params.get("plan_id") == plan.id


@pytest.mark.asyncio
class TestUpsertEnrollmentHistory:
    def _patch_all(self, service, student=None, course=None, degree=None):
        students = {student.doc_id: student} if student else {}
        courses = {course.code: course} if course else {}
        degrees = {degree.code: degree} if degree else {}
        return (
            patch.object(service, "_fetch_students", return_value=students),
            patch.object(service, "_fetch_courses", return_value=courses),
            patch.object(service, "_fetch_degrees", return_value=degrees),
        )

    async def test_skips_when_student_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        degree = make_degree("P")
        course = make_course("ALGO1")

        p1, p2, p3 = self._patch_all(service, student=None, course=course, degree=degree)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_enrollment_history([make_enrollment_history_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_skips_when_course_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        student = make_student("12345678")
        degree = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=student, course=None, degree=degree)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_enrollment_history([make_enrollment_history_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_upserts_when_all_refs_found(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        student = make_student("12345678")
        course = make_course("ALGO1")
        degree = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=student, course=course, degree=degree)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_enrollment_history([make_enrollment_history_row()])

        assert upserted == 1
        assert skipped == 0
        session.execute.assert_called_once()

    async def test_result_mapped_to_enrollment_status(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        student = make_student("12345678")
        course = make_course("ALGO1")
        degree = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=student, course=course, degree=degree)
        with p1, p2, p3:
            await service._upsert_enrollment_history([make_enrollment_history_row(result="A")])

        call_args = session.execute.call_args[0][0]
        assert call_args.compile().params.get("enrollment_status") == "aprobado"

    async def test_unknown_result_returns_unknown(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        student = make_student("12345678")
        course = make_course("ALGO1")
        degree = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=student, course=course, degree=degree)
        with p1, p2, p3:
            await service._upsert_enrollment_history([make_enrollment_history_row(result="X")])

        call_args = session.execute.call_args[0][0]
        assert call_args.compile().params.get("enrollment_status") == "__unknown__"


@pytest.mark.asyncio
class TestUpsertEnrollments:
    def _patch_all(self, service, student=None, course=None, degree=None):
        students = {student.doc_id: student} if student else {}
        courses = {course.code: course} if course else {}
        degrees = {degree.code: degree} if degree else {}
        return (
            patch.object(service, "_fetch_students", return_value=students),
            patch.object(service, "_fetch_courses", return_value=courses),
            patch.object(service, "_fetch_degrees", return_value=degrees),
        )

    async def test_skips_when_student_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        course = make_course("ALGO1")
        degree = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=None, course=course, degree=degree)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_enrollments([make_enrollment_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_skips_when_course_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        student = make_student("12345678")
        degree = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=student, course=None, degree=degree)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_enrollments([make_enrollment_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_skips_when_degree_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        student = make_student("12345678")
        course = make_course("ALGO1")

        p1, p2, p3 = self._patch_all(service, student=student, course=course, degree=None)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_enrollments([make_enrollment_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_upserts_with_status_inscripto(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        student = make_student("12345678")
        course = make_course("ALGO1")
        degree = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=student, course=course, degree=degree)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_enrollments([make_enrollment_row()])

        assert upserted == 1
        assert skipped == 0
        call_args = session.execute.call_args[0][0]
        assert call_args.compile().params.get("enrollment_status") == "inscripto"


@pytest.mark.asyncio
class TestUpsertDegrees:
    async def test_upserts_all_rows(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)

        upserted, skipped = await service._upsert_degrees([make_degree_row("TPI"), make_degree_row("LDS")])

        assert upserted == 2
        assert skipped == 0
        assert session.execute.call_count == 2

    async def test_commits_at_end(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)

        await service._upsert_degrees([make_degree_row()])

        session.commit.assert_called_once()


@pytest.mark.asyncio
class TestUpsertCourses:
    async def test_upserts_all_rows(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)

        upserted, skipped = await service._upsert_courses([make_course_row("101"), make_course_row("102")])

        assert upserted == 2
        assert skipped == 0
        assert session.execute.call_count == 2

    async def test_commits_at_end(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)

        await service._upsert_courses([make_course_row()])

        session.commit.assert_called_once()


@pytest.mark.asyncio
class TestUpsertStudyPlans:
    async def test_skips_when_degree_not_found(self):
        service = GuaraniImporterService(AsyncMock())

        with patch.object(service, "_fetch_degrees", return_value={}):
            with patch.object(service, "_fetch_courses", return_value={}):
                with patch.object(service, "_fetch_study_plans", return_value={}):
                    upserted, skipped = await service._upsert_study_plans([make_study_plan_course_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_skips_when_course_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        degree = make_degree("TPI")

        with patch.object(service, "_fetch_degrees", return_value={"TPI": degree}):
            with patch.object(service, "_fetch_courses", return_value={}):
                with patch.object(service, "_fetch_study_plans", return_value={}):
                    upserted, skipped = await service._upsert_study_plans([make_study_plan_course_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_upserts_when_refs_found(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        degree = make_degree("TPI")
        course = make_course("101")
        plan = make_study_plan(degree.id, 2015)

        with patch.object(service, "_fetch_degrees", return_value={"TPI": degree}):
            with patch.object(service, "_fetch_courses", return_value={"101": course}):
                with patch.object(service, "_fetch_study_plans", return_value={(degree.id, 2015): plan}):
                    upserted, skipped = await service._upsert_study_plans([make_study_plan_course_row()])

        assert upserted == 1
        assert skipped == 0

    async def test_commits_at_end(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        degree = make_degree("TPI")
        course = make_course("101")
        plan = make_study_plan(degree.id, 2015)

        with patch.object(service, "_fetch_degrees", return_value={"TPI": degree}):
            with patch.object(service, "_fetch_courses", return_value={"101": course}):
                with patch.object(service, "_fetch_study_plans", return_value={(degree.id, 2015): plan}):
                    await service._upsert_study_plans([make_study_plan_course_row()])

        session.commit.assert_called_once()


@pytest.mark.asyncio
class TestUpsertPrerequisites:
    async def test_skips_when_degree_not_found(self):
        service = GuaraniImporterService(AsyncMock())

        with patch.object(service, "_fetch_degrees", return_value={}):
            with patch.object(service, "_fetch_courses", return_value={}):
                with patch.object(service, "_fetch_study_plans", return_value={}):
                    upserted, skipped = await service._upsert_prerequisites([make_prerequisite_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_skips_when_plan_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        degree = make_degree("TPI")
        course = make_course("102")

        with patch.object(service, "_fetch_degrees", return_value={"TPI": degree}):
            with patch.object(service, "_fetch_courses", return_value={"102": course}):
                with patch.object(service, "_fetch_study_plans", return_value={}):
                    upserted, skipped = await service._upsert_prerequisites([make_prerequisite_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_upserts_required_prerequisites(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        degree = make_degree("TPI")
        course_102 = make_course("102")
        course_101 = make_course("101")
        plan = make_study_plan(degree.id, 2015)

        row = make_prerequisite_row(required_codes=["101"], recommended_codes=[])

        with patch.object(service, "_fetch_degrees", return_value={"TPI": degree}):
            with patch.object(service, "_fetch_courses", return_value={"102": course_102, "101": course_101}):
                with patch.object(service, "_fetch_study_plans", return_value={(degree.id, 2015): plan}):
                    upserted, skipped = await service._upsert_prerequisites([row])

        assert upserted == 1
        assert skipped == 0

    async def test_upserts_multiple_required_and_recommended(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        degree = make_degree("TPI")
        courses = {code: make_course(code) for code in ["102", "100", "101"]}
        plan = make_study_plan(degree.id, 2015)

        # "101" appears in both lists — required should win; dedup yields 2 unique entries
        row = make_prerequisite_row(required_codes=["100", "101"], recommended_codes=["101"])

        with patch.object(service, "_fetch_degrees", return_value={"TPI": degree}):
            with patch.object(service, "_fetch_courses", return_value=courses):
                with patch.object(service, "_fetch_study_plans", return_value={(degree.id, 2015): plan}):
                    upserted, skipped = await service._upsert_prerequisites([row])

        assert upserted == 2
        assert skipped == 0

    async def test_commits_at_end(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        degree = make_degree("TPI")
        course_102 = make_course("102")
        course_101 = make_course("101")
        plan = make_study_plan(degree.id, 2015)

        with patch.object(service, "_fetch_degrees", return_value={"TPI": degree}):
            with patch.object(service, "_fetch_courses", return_value={"102": course_102, "101": course_101}):
                with patch.object(service, "_fetch_study_plans", return_value={(degree.id, 2015): plan}):
                    await service._upsert_prerequisites([make_prerequisite_row()])

        session.commit.assert_called_once()
