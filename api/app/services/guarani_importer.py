import logging
import uuid
from pathlib import Path
from typing import Self

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import generate_uuid
from app.db.session import SessionDep
from app.importers.guarani.parsers import parse_students
from app.importers.guarani.types import StudentRow
from app.models.degree import Degree
from app.models.student import Student
from app.models.study_plan import StudyPlan

logger = logging.getLogger(__name__)


class GuaraniImporterService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @classmethod
    def dep(cls, session: SessionDep) -> Self:
        return cls(session)

    async def import_students(self, path: Path) -> tuple[int, int]:
        rows = parse_students(path)
        return await self._upsert_students(rows)

    async def _upsert_students(self, rows: list[StudentRow]) -> tuple[int, int]:
        degrees = await self._fetch_degrees()
        study_plans = await self._fetch_study_plans()

        upserted = 0
        skipped = 0

        for row in rows:
            degree = degrees.get(row.degree_code)
            if degree is None:
                logger.warning(
                    "import_students: degree '%s' not found — skipping doc_id=%s",
                    row.degree_code,
                    row.doc_id,
                )
                skipped += 1
                continue

            plan = study_plans.get((degree.id, row.study_plan_year))

            stmt = (
                insert(Student)
                .values(
                    id=generate_uuid(),
                    doc_id=row.doc_id,
                    unq_id=row.unq_id,
                    first_name=row.first_name,
                    last_name=row.last_name,
                    email=row.email,
                    enrolled_at=row.enrolled_at,
                    degree_id=degree.id,
                    plan_id=plan.id if plan else None,
                    academic_status="alumno_regular",
                )
                .on_conflict_do_update(
                    index_elements=["doc_id"],
                    set_={
                        "unq_id": row.unq_id,
                        "first_name": row.first_name,
                        "last_name": row.last_name,
                        "email": row.email,
                        "enrolled_at": row.enrolled_at,
                        "degree_id": degree.id,
                        "plan_id": plan.id if plan else None,
                    },
                )
            )
            await self.session.execute(stmt)
            upserted += 1

        await self.session.commit()
        return upserted, skipped

    async def _fetch_degrees(self) -> dict[str, Degree]:
        result = await self.session.execute(select(Degree))
        return {d.code: d for d in result.scalars().all()}

    async def _fetch_study_plans(self) -> dict[tuple[uuid.UUID, int], StudyPlan]:
        result = await self.session.execute(select(StudyPlan))
        return {(sp.degree_id, sp.year): sp for sp in result.scalars().all()}
