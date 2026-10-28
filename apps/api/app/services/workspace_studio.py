import uuid
from typing import Self

from db.models.alumno import Alumno
from db.models.alumno_carrera import AlumnoCarrera
from db.models.cursada import Cursada
from db.models.materia import Materia
from db.models.plan_de_estudio import PlanDeEstudio
from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from app.errors import NotFoundError
from app.session import SessionDep


def _search_tokens(column: InstrumentedAttribute[str], term: str) -> list[ColumnElement[bool]]:
    """Un `AND` por token, contra el `search_term` normalizado: "luci fer" encuentra "Fernández Lucía"."""
    return [column.like(func.f_unaccent(func.lower(f"%{_escape_like(t)}%")), escape="\\") for t in term.split()]


def _escape_like(token: str) -> str:
    """Los comodines que escribe el usuario son texto, no operadores."""
    return token.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class WorkspaceStudioService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @classmethod
    def dep(cls, session: SessionDep) -> Self:
        return cls(session)

    async def list_estudiantes(
        self,
        skip: int = 0,
        limit: int = 20,
        carrera_id: uuid.UUID | None = None,
        estado_academico: str | None = None,
    ) -> tuple[int, list[Alumno]]:
        id_q = select(AlumnoCarrera.alumno_id).distinct()
        if carrera_id is not None:
            id_q = id_q.join(AlumnoCarrera.plan).where(PlanDeEstudio.carrera_id == carrera_id)
        if estado_academico is not None:
            id_q = id_q.where(AlumnoCarrera.estado_academico == estado_academico)
        total = await self.session.scalar(select(func.count()).select_from(id_q.subquery())) or 0

        id_q = id_q.order_by(AlumnoCarrera.alumno_id).offset(skip).limit(limit)
        id_result = await self.session.execute(id_q)
        alumno_ids = [r[0] for r in id_result]

        if not alumno_ids:
            return total, []

        stmt = (
            select(Alumno)
            .where(Alumno.id.in_(alumno_ids))
            .options(selectinload(Alumno.carreras).selectinload(AlumnoCarrera.plan).selectinload(PlanDeEstudio.carrera))
            .order_by(Alumno.apellido, Alumno.nombre)
        )
        result = await self.session.execute(stmt)
        return total, list(result.scalars().all())

    async def list_materias(self, skip: int = 0, limit: int = 20) -> tuple[int, list[Materia]]:
        total = await self.session.scalar(select(func.count()).select_from(Materia)) or 0

        stmt = (
            select(Materia)
            .options(selectinload(Materia.planes).selectinload(PlanDeEstudio.carrera))
            .order_by(Materia.nombre)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return total, list(result.scalars().all())

    async def list_cursadas(
        self,
        skip: int = 0,
        limit: int = 20,
        carrera_id: uuid.UUID | None = None,
        alumno_id: uuid.UUID | None = None,
        alumno: str | None = None,
        materia: str | None = None,
        anio: int | None = None,
        cuatrimestre: str | None = None,
        estado_cursada: list[str] | None = None,
        tipo_cursada: str | None = None,
    ) -> tuple[int, list[Cursada]]:
        criteria = []
        if carrera_id is not None:
            criteria.append(Cursada.carrera_id == carrera_id)
        if alumno_id is not None:
            criteria.append(Cursada.alumno_id == alumno_id)
        if alumno:
            criteria.extend(_search_tokens(Alumno.search_term, alumno))
        if materia:
            criteria.extend(_search_tokens(Materia.search_term, materia))
        if anio is not None:
            criteria.append(Cursada.anio == anio)
        if cuatrimestre is not None:
            criteria.append(Cursada.cuatrimestre == cuatrimestre)
        if estado_cursada:
            criteria.append(Cursada.estado_cursada.in_(estado_cursada))
        if tipo_cursada is not None:
            criteria.append(Cursada.tipo_cursada == tipo_cursada)

        id_stmt = select(Cursada.id).join(Cursada.alumno).join(Cursada.materia).where(*criteria)
        total = await self.session.scalar(select(func.count()).select_from(id_stmt.subquery())) or 0
        return total, await self._fetch_cursadas(criteria, skip, limit)

    async def _fetch_cursadas(self, criteria: list[ColumnElement[bool]], skip: int, limit: int) -> list[Cursada]:
        stmt = (
            select(Cursada)
            .join(Cursada.alumno)
            .join(Cursada.materia)
            .where(*criteria)
            .options(*_CURSADA_REFS)
            .order_by(*_CURSADA_ORDER)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_estudiante_detalle(self, alumno_id: uuid.UUID) -> tuple[Alumno, list[Cursada]]:
        stmt = (
            select(Alumno)
            .where(Alumno.id == alumno_id)
            .options(selectinload(Alumno.carreras).selectinload(AlumnoCarrera.plan).selectinload(PlanDeEstudio.carrera))
        )
        alumno = (await self.session.execute(stmt)).scalar_one_or_none()
        if alumno is None:
            raise NotFoundError("alumnos", alumno_id)

        cursadas = await self._fetch_cursadas([Cursada.alumno_id == alumno_id], 0, _HISTORIAL_LIMIT)
        return alumno, cursadas


# shortcut: historial del modal topeado en 200 filas (un plan de grado ronda 40);
# paginar el modal si alguna carrera pasa ese techo.
_HISTORIAL_LIMIT = 200

_CURSADA_REFS = (
    selectinload(Cursada.alumno),
    selectinload(Cursada.materia),
    selectinload(Cursada.carrera),
)

_CURSADA_ORDER = (
    Cursada.anio.desc(),
    Cursada.cuatrimestre.desc(),
    Materia.nombre,
    Cursada.id,
)
