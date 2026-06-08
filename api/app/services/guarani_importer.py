import logging
import uuid
from pathlib import Path
from typing import Self

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import generate_uuid
from app.db.session import SessionDep
from app.importers.guarani.parsers import (
    parse_courses,
    parse_degrees,
    parse_enrollment_history,
    parse_enrollments,
    parse_prerequisites,
    parse_students,
    parse_study_plan_courses,
)
from app.importers.guarani.types import (
    CourseRow,
    DegreeRow,
    EnrollmentHistoryRow,
    EnrollmentRow,
    PrerequisiteRow,
    StudentRow,
    StudyPlanCourseRow,
)
from app.importers.utils import date_to_year_term
from app.models.alumno import Alumno
from app.models.alumno_carrera import AlumnoCarrera
from app.models.carrera import Carrera
from app.models.correlativa import Correlativa
from app.models.cursada import Cursada
from app.models.materia import Materia
from app.models.plan_de_estudio import PlanDeEstudio
from app.models.planes_materias import planes_materias

logger = logging.getLogger(__name__)

_RESULT_TO_STATUS: dict[str, str] = {
    "I": "inscripto",
    "P": "promocionado",
    "A": "aprobado",
    "D": "desaprobado",
    "R": "regular",
    "PA": "pendiente_aprobacion",
}


def _result_to_status(result: str) -> str:
    code = result.strip().upper()
    return _RESULT_TO_STATUS.get(code, "__unknown__")


class GuaraniImporterService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @classmethod
    def dep(cls, session: SessionDep) -> Self:
        return cls(session)

    async def import_degrees(self, path: Path) -> tuple[int, int]:
        rows = parse_degrees(path)
        return await self._upsert_carreras(rows)

    async def import_courses(self, path: Path) -> tuple[int, int]:
        rows = parse_courses(path)
        return await self._upsert_materias(rows)

    async def import_study_plans(self, paths: list[Path]) -> tuple[int, int]:
        rows: list[StudyPlanCourseRow] = []
        for path in paths:
            rows.extend(parse_study_plan_courses(path))
        return await self._upsert_planes(rows)

    async def import_prerequisites(self, paths: list[Path]) -> tuple[int, int]:
        rows: list[PrerequisiteRow] = []
        for path in paths:
            rows.extend(parse_prerequisites(path))
        return await self._upsert_correlativas(rows)

    async def import_students(self, path: Path) -> tuple[int, int]:
        rows = parse_students(path)
        return await self._upsert_alumnos(rows)

    async def import_enrollment_history(self, path: Path) -> tuple[int, int]:
        rows = parse_enrollment_history(path)
        return await self._upsert_historial_cursadas(rows)

    async def import_enrollments(self, path: Path) -> tuple[int, int]:
        rows = parse_enrollments(path)
        return await self._upsert_cursadas(rows)

    async def _upsert_alumnos(self, rows: list[StudentRow]) -> tuple[int, int]:
        carreras = await self._fetch_carreras()
        planes = await self._fetch_planes()

        upserted = 0
        skipped = 0

        for row in rows:
            carrera = carreras.get(row.degree_code)
            if carrera is None:
                logger.warning(
                    "import_students: carrera '%s' not found — skipping doc_id=%s",
                    row.degree_code,
                    row.doc_id,
                )
                skipped += 1
                continue

            plan = planes.get((carrera.id, row.study_plan_year))
            if plan is None:
                logger.warning(
                    "import_students: plan year=%s not found for carrera '%s' — skipping enrollment for doc_id=%s",
                    row.study_plan_year,
                    row.degree_code,
                    row.doc_id,
                )
                skipped += 1
                continue

            alumno_id = generate_uuid()
            stmt_alumno = (
                insert(Alumno)
                .values(
                    id=alumno_id,
                    dni=row.doc_id,
                    legajo=row.unq_id,
                    nombre=row.first_name,
                    apellido=row.last_name,
                    email=row.email,
                )
                .on_conflict_do_update(
                    index_elements=["dni"],
                    set_={
                        "legajo": row.unq_id,
                        "nombre": row.first_name,
                        "apellido": row.last_name,
                        "email": row.email,
                        "updated_at": func.now(),
                    },
                )
                .returning(Alumno.id)
            )
            result = await self.session.execute(stmt_alumno)
            alumno_id = result.scalar_one()

            stmt_carrera = (
                insert(AlumnoCarrera)
                .values(
                    alumno_id=alumno_id,
                    plan_id=plan.id,
                    fecha_ingreso=row.enrolled_at,
                    estado_academico="alumno_regular",
                )
                .on_conflict_do_update(
                    index_elements=["alumno_id", "plan_id"],
                    set_={  # estado_academico intentionally absent: preserve manual overrides
                        "fecha_ingreso": row.enrolled_at,
                        "updated_at": func.now(),
                    },
                )
            )
            await self.session.execute(stmt_carrera)
            upserted += 1

        await self.session.commit()
        return upserted, skipped

    async def _upsert_historial_cursadas(self, rows: list[EnrollmentHistoryRow]) -> tuple[int, int]:
        alumnos = await self._fetch_alumnos()
        materias = await self._fetch_materias()
        carreras = await self._fetch_carreras()

        upserted = 0
        skipped = 0

        for row in rows:
            alumno = alumnos.get(row.doc_id)
            materia = materias.get(row.course_code)
            carrera = carreras.get(row.degree_code)

            if alumno is None or materia is None or carrera is None:
                logger.warning(
                    "import_enrollment_history: missing refs — skipping doc_id=%s course=%s degree=%s",
                    row.doc_id,
                    row.course_code,
                    row.degree_code,
                )
                skipped += 1
                continue

            anio, cuatrimestre = date_to_year_term(row.enrollment_date)
            estado = _result_to_status(row.result)

            stmt = (
                insert(Cursada)
                .values(
                    id=generate_uuid(),
                    alumno_id=alumno.id,
                    materia_id=materia.id,
                    carrera_id=carrera.id,
                    anio=anio,
                    cuatrimestre=cuatrimestre,
                    tipo_cursada=row.enrollment_type,
                    estado_cursada=estado,
                    nota=row.grade,
                    fecha_inscripcion=row.enrollment_date,
                    es_regular=row.is_regular,
                    tipo_aprobacion=row.approval_type,
                    anio_plan=row.plan_year,
                )
                .on_conflict_do_update(
                    constraint="uq_cursada_alumno_materia_carrera_cuatrimestre",
                    set_={
                        "estado_cursada": estado,
                        "nota": row.grade,
                        "fecha_inscripcion": row.enrollment_date,
                        "es_regular": row.is_regular,
                        "tipo_aprobacion": row.approval_type,
                        "anio_plan": row.plan_year,
                        "updated_at": func.now(),
                    },
                )
            )
            await self.session.execute(stmt)
            upserted += 1

        await self.session.commit()
        return upserted, skipped

    async def _upsert_cursadas(self, rows: list[EnrollmentRow]) -> tuple[int, int]:
        alumnos = await self._fetch_alumnos()
        materias = await self._fetch_materias()
        carreras = await self._fetch_carreras()

        upserted = 0
        skipped = 0

        for row in rows:
            alumno = alumnos.get(row.doc_id)
            materia = materias.get(row.course_code)
            carrera = carreras.get(row.degree_code)

            if alumno is None or materia is None or carrera is None:
                logger.warning(
                    "import_enrollments: missing refs — skipping doc_id=%s course=%s degree=%s",
                    row.doc_id,
                    row.course_code,
                    row.degree_code,
                )
                skipped += 1
                continue

            anio, cuatrimestre = date_to_year_term(row.enrollment_date)

            stmt = (
                insert(Cursada)
                .values(
                    id=generate_uuid(),
                    alumno_id=alumno.id,
                    materia_id=materia.id,
                    carrera_id=carrera.id,
                    anio=anio,
                    cuatrimestre=cuatrimestre,
                    comision=row.section,
                    tipo_cursada="regular",
                    estado_cursada="inscripto",
                    fecha_inscripcion=row.enrollment_date,
                )
                .on_conflict_do_update(
                    constraint="uq_cursada_alumno_materia_carrera_cuatrimestre",
                    set_={
                        "comision": row.section,
                        "fecha_inscripcion": row.enrollment_date,
                        "updated_at": func.now(),
                    },
                )
            )
            await self.session.execute(stmt)
            upserted += 1

        await self.session.commit()
        return upserted, skipped

    async def _upsert_carreras(self, rows: list[DegreeRow]) -> tuple[int, int]:
        for row in rows:
            stmt = (
                insert(Carrera)
                .values(id=generate_uuid(), codigo=row.code, nombre=row.name)
                .on_conflict_do_update(
                    index_elements=["codigo"],
                    set_={"nombre": row.name, "updated_at": func.now()},
                )
            )
            await self.session.execute(stmt)
        await self.session.commit()
        return len(rows), 0

    async def _upsert_materias(self, rows: list[CourseRow]) -> tuple[int, int]:
        for row in rows:
            stmt = (
                insert(Materia)
                .values(id=generate_uuid(), codigo=row.code, nombre=row.name, sigla=row.abbreviation)
                .on_conflict_do_update(
                    index_elements=["codigo"],
                    set_={"nombre": row.name, "sigla": row.abbreviation, "updated_at": func.now()},
                )
            )
            await self.session.execute(stmt)
        await self.session.commit()
        return len(rows), 0

    async def _upsert_planes(self, rows: list[StudyPlanCourseRow]) -> tuple[int, int]:
        carreras = await self._fetch_carreras()
        materias = await self._fetch_materias()

        seen: set[tuple[str, int]] = set()
        for row in rows:
            carrera = carreras.get(row.degree_code)
            if carrera is None:
                continue
            key = (row.degree_code, row.plan_year)
            if key in seen:
                continue
            seen.add(key)
            stmt = (
                insert(PlanDeEstudio)
                .values(
                    id=generate_uuid(),
                    carrera_id=carrera.id,
                    nombre=f"Plan {row.plan_year}",
                    anio=row.plan_year,
                )
                .on_conflict_do_update(
                    constraint="uq_plan_carrera_anio",
                    set_={"updated_at": func.now()},
                )
            )
            await self.session.execute(stmt)
        await self.session.flush()

        planes = await self._fetch_planes()
        upserted = 0
        skipped = 0

        for row in rows:
            carrera = carreras.get(row.degree_code)
            materia = materias.get(row.course_code)
            if carrera is None or materia is None:
                logger.warning(
                    "import_study_plans: missing refs — skipping degree=%s course=%s",
                    row.degree_code,
                    row.course_code,
                )
                skipped += 1
                continue
            plan = planes.get((carrera.id, row.plan_year))
            if plan is None:
                logger.warning(
                    "import_study_plans: plan not found after upsert — degree=%s year=%d",
                    row.degree_code,
                    row.plan_year,
                )
                skipped += 1
                continue
            link_stmt = insert(planes_materias).values(plan_id=plan.id, materia_id=materia.id).on_conflict_do_nothing()
            await self.session.execute(link_stmt)
            upserted += 1

        await self.session.commit()
        return upserted, skipped

    async def _upsert_correlativas(self, rows: list[PrerequisiteRow]) -> tuple[int, int]:
        materias = await self._fetch_materias()

        upserted = 0
        skipped = 0

        for row in rows:
            materia = materias.get(row.course_code)
            if materia is None:
                logger.warning("import_prerequisites: materia not found — code=%s", row.course_code)
                skipped += 1
                continue

            # required_codes overwrite recommended_codes when a code appears in both
            prereqs: dict[str, bool] = {code: False for code in row.recommended_codes}
            prereqs.update({code: True for code in row.required_codes})
            for prereq_code, es_obligatoria in prereqs.items():
                prereq = materias.get(prereq_code)
                if prereq is None:
                    logger.warning("_upsert_correlativas: materia requerida not found — code=%s", prereq_code)
                    skipped += 1
                    continue
                stmt = (
                    insert(Correlativa)
                    .values(
                        materia_id=materia.id,
                        requisito_id=prereq.id,
                        es_obligatoria=es_obligatoria,
                    )
                    .on_conflict_do_update(
                        index_elements=["materia_id", "requisito_id"],
                        set_={"es_obligatoria": es_obligatoria, "updated_at": func.now()},
                    )
                )
                await self.session.execute(stmt)
                upserted += 1

        await self.session.commit()
        return upserted, skipped

    async def _fetch_carreras(self) -> dict[str, Carrera]:
        result = await self.session.execute(select(Carrera))
        return {c.codigo: c for c in result.scalars().all()}

    async def _fetch_planes(self) -> dict[tuple[uuid.UUID, int], PlanDeEstudio]:
        result = await self.session.execute(select(PlanDeEstudio))
        return {(p.carrera_id, p.anio): p for p in result.scalars().all()}

    async def _fetch_alumnos(self) -> dict[str, Alumno]:
        result = await self.session.execute(select(Alumno))
        return {a.dni: a for a in result.scalars().all()}

    async def _fetch_materias(self) -> dict[str, Materia]:
        result = await self.session.execute(select(Materia))
        return {m.codigo: m for m in result.scalars().all()}
