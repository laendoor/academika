import uuid
from typing import Self

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import SessionDep
from app.models.alumno import Alumno
from app.models.alumno_carrera import AlumnoCarrera
from app.models.materia import Materia
from app.models.plan_de_estudio import PlanDeEstudio


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
