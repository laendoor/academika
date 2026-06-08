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
class TestUpsertAlumnos:
    async def test_skips_when_carrera_not_found(self):
        service = GuaraniImporterService(AsyncMock())

        with patch.object(service, "_fetch_carreras", return_value={}):
            with patch.object(service, "_fetch_planes", return_value={}):
                upserted, skipped = await service._upsert_alumnos([make_student_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_upserts_when_carrera_and_plan_found(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        carrera = make_degree("P")
        plan = make_study_plan(carrera.id, year=2015)

        with patch.object(service, "_fetch_carreras", return_value={"P": carrera}):
            with patch.object(service, "_fetch_planes", return_value={(carrera.id, 2015): plan}):
                upserted, skipped = await service._upsert_alumnos([make_student_row(degree_code="P")])

        assert upserted == 1
        assert skipped == 0
        assert session.execute.call_count == 2  # alumno + alumno_carrera

    async def test_commits_at_end(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        carrera = make_degree("P")

        with patch.object(service, "_fetch_carreras", return_value={"P": carrera}):
            with patch.object(service, "_fetch_planes", return_value={}):
                await service._upsert_alumnos([make_student_row()])

        session.commit.assert_called_once()

    async def test_mixed_rows_correct_counts(self):
        service = GuaraniImporterService(AsyncMock())
        carrera = make_degree("P")
        plan = make_study_plan(carrera.id, year=2015)

        rows = [
            make_student_row(doc_id="111", degree_code="P"),
            make_student_row(doc_id="222", degree_code="X"),  # missing carrera → skip
            make_student_row(doc_id="333", degree_code="P"),
        ]

        with patch.object(service, "_fetch_carreras", return_value={"P": carrera}):
            with patch.object(service, "_fetch_planes", return_value={(carrera.id, 2015): plan}):
                upserted, skipped = await service._upsert_alumnos(rows)

        assert upserted == 2
        assert skipped == 1

    async def test_skips_when_plan_not_found(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        carrera = make_degree("P")

        with patch.object(service, "_fetch_carreras", return_value={"P": carrera}):
            with patch.object(service, "_fetch_planes", return_value={}):
                upserted, skipped = await service._upsert_alumnos([make_student_row(plan_year=9999)])

        assert upserted == 0
        assert skipped == 1
        session.execute.assert_not_called()

    async def test_plan_id_set_when_plan_found(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        carrera = make_degree("P")
        plan = make_study_plan(carrera.id, year=2015)

        with patch.object(service, "_fetch_carreras", return_value={"P": carrera}):
            with patch.object(service, "_fetch_planes", return_value={(carrera.id, 2015): plan}):
                await service._upsert_alumnos([make_student_row(plan_year=2015)])

        call_args = session.execute.call_args[0][0]
        assert call_args.compile().params.get("plan_id") == plan.id


@pytest.mark.asyncio
class TestUpsertHistorialCursadas:
    def _patch_all(self, service, student=None, course=None, degree=None):
        alumnos = {student.doc_id: student} if student else {}
        materias = {course.code: course} if course else {}
        carreras = {degree.code: degree} if degree else {}
        return (
            patch.object(service, "_fetch_alumnos", return_value=alumnos),
            patch.object(service, "_fetch_materias", return_value=materias),
            patch.object(service, "_fetch_carreras", return_value=carreras),
        )

    async def test_skips_when_alumno_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        carrera = make_degree("P")
        materia = make_course("ALGO1")

        p1, p2, p3 = self._patch_all(service, student=None, course=materia, degree=carrera)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_historial_cursadas([make_enrollment_history_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_skips_when_materia_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        alumno = make_student("12345678")
        carrera = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=alumno, course=None, degree=carrera)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_historial_cursadas([make_enrollment_history_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_upserts_when_all_refs_found(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        alumno = make_student("12345678")
        materia = make_course("ALGO1")
        carrera = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=alumno, course=materia, degree=carrera)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_historial_cursadas([make_enrollment_history_row()])

        assert upserted == 1
        assert skipped == 0
        session.execute.assert_called_once()

    async def test_result_mapped_to_estado_cursada(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        alumno = make_student("12345678")
        materia = make_course("ALGO1")
        carrera = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=alumno, course=materia, degree=carrera)
        with p1, p2, p3:
            await service._upsert_historial_cursadas([make_enrollment_history_row(result="A")])

        call_args = session.execute.call_args[0][0]
        assert call_args.compile().params.get("estado_cursada") == "aprobado"

    async def test_unknown_result_returns_unknown(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        alumno = make_student("12345678")
        materia = make_course("ALGO1")
        carrera = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=alumno, course=materia, degree=carrera)
        with p1, p2, p3:
            await service._upsert_historial_cursadas([make_enrollment_history_row(result="X")])

        call_args = session.execute.call_args[0][0]
        assert call_args.compile().params.get("estado_cursada") == "__unknown__"


@pytest.mark.asyncio
class TestUpsertCursadas:
    def _patch_all(self, service, student=None, course=None, degree=None):
        alumnos = {student.doc_id: student} if student else {}
        materias = {course.code: course} if course else {}
        carreras = {degree.code: degree} if degree else {}
        return (
            patch.object(service, "_fetch_alumnos", return_value=alumnos),
            patch.object(service, "_fetch_materias", return_value=materias),
            patch.object(service, "_fetch_carreras", return_value=carreras),
        )

    async def test_skips_when_alumno_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        materia = make_course("ALGO1")
        carrera = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=None, course=materia, degree=carrera)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_cursadas([make_enrollment_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_skips_when_materia_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        alumno = make_student("12345678")
        carrera = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=alumno, course=None, degree=carrera)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_cursadas([make_enrollment_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_skips_when_carrera_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        alumno = make_student("12345678")
        materia = make_course("ALGO1")

        p1, p2, p3 = self._patch_all(service, student=alumno, course=materia, degree=None)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_cursadas([make_enrollment_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_upserts_with_estado_inscripto(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        alumno = make_student("12345678")
        materia = make_course("ALGO1")
        carrera = make_degree("P")

        p1, p2, p3 = self._patch_all(service, student=alumno, course=materia, degree=carrera)
        with p1, p2, p3:
            upserted, skipped = await service._upsert_cursadas([make_enrollment_row()])

        assert upserted == 1
        assert skipped == 0
        call_args = session.execute.call_args[0][0]
        assert call_args.compile().params.get("estado_cursada") == "inscripto"


@pytest.mark.asyncio
class TestUpsertCarreras:
    async def test_upserts_all_rows(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)

        upserted, skipped = await service._upsert_carreras([make_degree_row("TPI"), make_degree_row("LDS")])

        assert upserted == 2
        assert skipped == 0
        assert session.execute.call_count == 2

    async def test_commits_at_end(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)

        await service._upsert_carreras([make_degree_row()])

        session.commit.assert_called_once()


@pytest.mark.asyncio
class TestUpsertMaterias:
    async def test_upserts_all_rows(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)

        upserted, skipped = await service._upsert_materias([make_course_row("101"), make_course_row("102")])

        assert upserted == 2
        assert skipped == 0
        assert session.execute.call_count == 2

    async def test_commits_at_end(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)

        await service._upsert_materias([make_course_row()])

        session.commit.assert_called_once()


@pytest.mark.asyncio
class TestUpsertPlanes:
    async def test_skips_when_carrera_not_found(self):
        service = GuaraniImporterService(AsyncMock())

        with patch.object(service, "_fetch_carreras", return_value={}):
            with patch.object(service, "_fetch_materias", return_value={}):
                with patch.object(service, "_fetch_planes", return_value={}):
                    upserted, skipped = await service._upsert_planes([make_study_plan_course_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_skips_when_materia_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        carrera = make_degree("TPI")

        with patch.object(service, "_fetch_carreras", return_value={"TPI": carrera}):
            with patch.object(service, "_fetch_materias", return_value={}):
                with patch.object(service, "_fetch_planes", return_value={}):
                    upserted, skipped = await service._upsert_planes([make_study_plan_course_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_upserts_when_refs_found(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        carrera = make_degree("TPI")
        materia = make_course("101")
        plan = make_study_plan(carrera.id, 2015)

        with patch.object(service, "_fetch_carreras", return_value={"TPI": carrera}):
            with patch.object(service, "_fetch_materias", return_value={"101": materia}):
                with patch.object(service, "_fetch_planes", return_value={(carrera.id, 2015): plan}):
                    upserted, skipped = await service._upsert_planes([make_study_plan_course_row()])

        assert upserted == 1
        assert skipped == 0

    async def test_commits_at_end(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        carrera = make_degree("TPI")
        materia = make_course("101")
        plan = make_study_plan(carrera.id, 2015)

        with patch.object(service, "_fetch_carreras", return_value={"TPI": carrera}):
            with patch.object(service, "_fetch_materias", return_value={"101": materia}):
                with patch.object(service, "_fetch_planes", return_value={(carrera.id, 2015): plan}):
                    await service._upsert_planes([make_study_plan_course_row()])

        session.commit.assert_called_once()


@pytest.mark.asyncio
class TestUpsertCorrelativas:
    async def test_skips_when_carrera_not_found(self):
        service = GuaraniImporterService(AsyncMock())

        with patch.object(service, "_fetch_carreras", return_value={}):
            with patch.object(service, "_fetch_materias", return_value={}):
                with patch.object(service, "_fetch_planes", return_value={}):
                    upserted, skipped = await service._upsert_correlativas([make_prerequisite_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_skips_when_plan_not_found(self):
        service = GuaraniImporterService(AsyncMock())
        carrera = make_degree("TPI")
        materia = make_course("102")

        with patch.object(service, "_fetch_carreras", return_value={"TPI": carrera}):
            with patch.object(service, "_fetch_materias", return_value={"102": materia}):
                with patch.object(service, "_fetch_planes", return_value={}):
                    upserted, skipped = await service._upsert_correlativas([make_prerequisite_row()])

        assert upserted == 0
        assert skipped == 1

    async def test_upserts_required_prerequisites(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        carrera = make_degree("TPI")
        materia_102 = make_course("102")
        materia_101 = make_course("101")
        plan = make_study_plan(carrera.id, 2015)

        row = make_prerequisite_row(required_codes=["101"], recommended_codes=[])

        with patch.object(service, "_fetch_carreras", return_value={"TPI": carrera}):
            with patch.object(service, "_fetch_materias", return_value={"102": materia_102, "101": materia_101}):
                with patch.object(service, "_fetch_planes", return_value={(carrera.id, 2015): plan}):
                    upserted, skipped = await service._upsert_correlativas([row])

        assert upserted == 1
        assert skipped == 0

    async def test_upserts_multiple_required_and_recommended(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        carrera = make_degree("TPI")
        materias = {code: make_course(code) for code in ["102", "100", "101"]}
        plan = make_study_plan(carrera.id, 2015)

        # "101" appears in both lists — required should win; dedup yields 2 unique entries
        row = make_prerequisite_row(required_codes=["100", "101"], recommended_codes=["101"])

        with patch.object(service, "_fetch_carreras", return_value={"TPI": carrera}):
            with patch.object(service, "_fetch_materias", return_value=materias):
                with patch.object(service, "_fetch_planes", return_value={(carrera.id, 2015): plan}):
                    upserted, skipped = await service._upsert_correlativas([row])

        assert upserted == 2
        assert skipped == 0

    async def test_commits_at_end(self):
        session = AsyncMock()
        service = GuaraniImporterService(session)
        carrera = make_degree("TPI")
        materia_102 = make_course("102")
        materia_101 = make_course("101")
        plan = make_study_plan(carrera.id, 2015)

        with patch.object(service, "_fetch_carreras", return_value={"TPI": carrera}):
            with patch.object(service, "_fetch_materias", return_value={"102": materia_102, "101": materia_101}):
                with patch.object(service, "_fetch_planes", return_value={(carrera.id, 2015): plan}):
                    await service._upsert_correlativas([make_prerequisite_row()])

        session.commit.assert_called_once()
