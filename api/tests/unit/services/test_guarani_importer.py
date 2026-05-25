from unittest.mock import AsyncMock, patch

import pytest

from app.services.guarani_importer import GuaraniImporterService
from tests.unit.factories import make_degree, make_student_row, make_study_plan


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
