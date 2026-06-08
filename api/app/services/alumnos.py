import uuid
from typing import Self

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionDep
from app.errors import ConflictError
from app.models.alumno import Alumno
from app.models.alumno_carrera import AlumnoCarrera
from app.schemas.alumnos import AlumnoCarreraCreate, AlumnoCreate, AlumnoUpdate
from app.services.base import BaseService


class AlumnoService(BaseService[Alumno, AlumnoCreate, AlumnoUpdate]):
    model = Alumno

    @classmethod
    def dep(cls, session: SessionDep) -> Self:
        return cls(session)

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
