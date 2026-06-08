import uuid

from sqlalchemy import delete, insert
from sqlalchemy.exc import IntegrityError

from app.db.base import generate_uuid
from app.errors import ConflictError
from app.models.plan_de_estudio import PlanDeEstudio
from app.models.planes_materias import planes_materias
from app.schemas.planes_de_estudio import PlanDeEstudioCreate, PlanDeEstudioUpdate
from app.services.base import BaseService


class PlanDeEstudioService(BaseService[PlanDeEstudio, PlanDeEstudioCreate, PlanDeEstudioUpdate]):
    model = PlanDeEstudio

    async def create(self, data: PlanDeEstudioCreate) -> PlanDeEstudio:
        materia_ids = data.materia_ids
        payload = data.model_dump(exclude={"materia_ids"})
        instance = PlanDeEstudio(id=generate_uuid(), **payload)
        self.session.add(instance)
        try:
            await self.session.flush()
            await self._set_materias(instance.id, materia_ids)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(str(e.orig)) from e
        await self.session.refresh(instance)
        return instance

    async def update(self, id: uuid.UUID, data: PlanDeEstudioUpdate) -> PlanDeEstudio:
        instance = await self.get_by_id(id)
        update_data = data.model_dump(exclude_none=True, exclude={"materia_ids"})
        for field, value in update_data.items():
            setattr(instance, field, value)
        try:
            if data.materia_ids is not None:
                await self._set_materias(instance.id, data.materia_ids)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(str(e.orig)) from e
        await self.session.refresh(instance)
        return instance

    async def _set_materias(self, plan_id: uuid.UUID, materia_ids: list[uuid.UUID]) -> None:
        await self.session.execute(delete(planes_materias).where(planes_materias.c.plan_id == plan_id))
        if materia_ids:
            await self.session.execute(
                insert(planes_materias).values([{"plan_id": plan_id, "materia_id": mid} for mid in materia_ids])
            )
