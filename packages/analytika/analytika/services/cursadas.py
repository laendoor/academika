import uuid
from datetime import date
from typing import Any

from db.models.carrera import Carrera
from db.models.cursada import Cursada
from db.models.materia import Materia
from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession


class CursadaService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def historia(self, alumno_id: uuid.UUID, carrera: str | None = None) -> list[Any]:
        stmt = (
            select(Cursada, Materia, Carrera)
            .join(Materia, Cursada.materia_id == Materia.id)
            .join(Carrera, Cursada.carrera_id == Carrera.id)
            .where(Cursada.alumno_id == alumno_id)
            .order_by(Carrera.codigo, Cursada.fecha_inscripcion, Materia.codigo)
        )
        if carrera is not None:
            stmt = stmt.where(Carrera.codigo == carrera)
        return list((await self.session.execute(stmt)).all())

    async def notas_de_carrera(self, alumno_id: uuid.UUID, carrera_id: uuid.UUID) -> list[tuple[uuid.UUID, str | None]]:
        rows = await self.session.execute(
            select(Cursada.materia_id, Cursada.nota).where(
                Cursada.alumno_id == alumno_id,
                Cursada.carrera_id == carrera_id,
            )
        )
        return list(rows.all())

    async def notas_cohorte(
        self, pairs: Select[tuple[uuid.UUID, uuid.UUID]]
    ) -> list[tuple[uuid.UUID, int, str, str | None, date | None]]:
        cohorte = pairs.subquery()
        stmt = select(
            Cursada.alumno_id, Cursada.anio, Cursada.cuatrimestre, Cursada.nota, Cursada.fecha_inscripcion
        ).join(
            cohorte,
            and_(Cursada.alumno_id == cohorte.c.alumno_id, Cursada.carrera_id == cohorte.c.carrera_id),
        )
        return list((await self.session.execute(stmt)).all())
