import uuid
from typing import Any

from db.models.alumno import Alumno
from db.models.alumno_carrera import AlumnoCarrera
from db.models.carrera import Carrera
from db.models.plan_de_estudio import PlanDeEstudio
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from analytika.utils.fechas import parse_year


class AlumnoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_dni(self, dni: str) -> Alumno | None:
        return await self.session.scalar(select(Alumno).where(Alumno.dni == dni))

    async def pares(self, alumno_id: uuid.UUID, carrera: str | None = None) -> list[Any]:
        """Un plan por carrera: el vigente y, si hay varios, el año más nuevo."""
        stmt = (
            select(PlanDeEstudio, Carrera)
            .join(AlumnoCarrera, AlumnoCarrera.plan_id == PlanDeEstudio.id)
            .join(Carrera, PlanDeEstudio.carrera_id == Carrera.id)
            .where(AlumnoCarrera.alumno_id == alumno_id)
            .order_by(Carrera.codigo, PlanDeEstudio.vigente.desc(), PlanDeEstudio.anio.desc())
        )
        if carrera is not None:
            stmt = stmt.where(Carrera.codigo == carrera)
        elegidos: dict[uuid.UUID, Any] = {}
        for plan, plan_carrera in (await self.session.execute(stmt)).all():
            elegidos.setdefault(plan_carrera.id, (plan, plan_carrera))
        return list(elegidos.values())

    @staticmethod
    def pares_cohorte_query(
        carrera: str | None, ingreso: str | None, estado: str | None, plan: str | None
    ) -> Select[tuple[uuid.UUID, uuid.UUID]]:
        """Pares (alumno, carrera) que matchean los filtros de una cohorte."""
        stmt = (
            select(AlumnoCarrera.alumno_id, PlanDeEstudio.carrera_id)
            .join(PlanDeEstudio, AlumnoCarrera.plan_id == PlanDeEstudio.id)
            .distinct()
        )
        if carrera is not None:
            stmt = stmt.join(Carrera, PlanDeEstudio.carrera_id == Carrera.id).where(Carrera.codigo == carrera)
        if ingreso is not None:
            stmt = stmt.where(func.extract("year", AlumnoCarrera.fecha_ingreso) == parse_year(ingreso, "ingreso"))
        if estado is not None:
            stmt = stmt.where(AlumnoCarrera.estado_academico == estado)
        if plan is not None:
            stmt = stmt.where(PlanDeEstudio.anio == parse_year(plan, "plan"))
        return stmt
