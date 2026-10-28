import uuid
from typing import Self

from db.models.alumno import Alumno
from db.models.alumno_carrera import AlumnoCarrera
from db.search import search_criteria
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.errors import ConflictError
from app.schemas.alumnos import AlumnoCarreraCreate, AlumnoCreate, AlumnoUpdate
from app.services.base import BaseService
from app.session import SessionDep


class AlumnoService(BaseService[Alumno, AlumnoCreate, AlumnoUpdate]):
    model = Alumno

    @classmethod
    def dep(cls, session: SessionDep) -> Self:
        return cls(session)

    async def search(self, q: str, limit: int = 8) -> list[Alumno]:
        criteria = search_criteria(Alumno.search_term, q)
        if not criteria:
            return []
        stmt = select(Alumno).where(*criteria).order_by(Alumno.apellido, Alumno.nombre).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_carreras(self, alumno_id: uuid.UUID) -> list[AlumnoCarrera]:
        await self.get_by_id(alumno_id)
        result = await self.session.execute(select(AlumnoCarrera).where(AlumnoCarrera.alumno_id == alumno_id))
        return list(result.scalars().all())

    async def add_carrera(self, alumno_id: uuid.UUID, data: AlumnoCarreraCreate) -> AlumnoCarrera:
        await self.get_by_id(alumno_id)
        instance = AlumnoCarrera(alumno_id=alumno_id, **data.model_dump())
        self.session.add(instance)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(str(e.orig)) from e
        await self.session.refresh(instance)
        return instance
