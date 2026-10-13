import uuid

from sqlalchemy import delete, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from app.db.base import generate_uuid
from app.errors import ConflictError, NotFoundError
from app.models.plan_de_estudio import PlanDeEstudio
from app.models.planes_materias import planes_materias
from app.schemas.planes_de_estudio import PlanDeEstudioCreate, PlanDeEstudioUpdate
from app.services.base import BaseService


class PlanDeEstudioService(BaseService[PlanDeEstudio, PlanDeEstudioCreate, PlanDeEstudioUpdate]):
    model = PlanDeEstudio

    async def get_detail(self, plan_id: uuid.UUID) -> PlanDeEstudio:
        result = await self.session.execute(
            select(PlanDeEstudio)
            .options(selectinload(PlanDeEstudio.materias), joinedload(PlanDeEstudio.carrera))
            .where(PlanDeEstudio.id == plan_id)
        )
        instance = result.scalars().first()
        if instance is None:
            raise NotFoundError(PlanDeEstudio.__tablename__, plan_id)
        return instance

    async def list_filtered(
        self, skip: int = 0, limit: int = 20, carrera_id: uuid.UUID | None = None
    ) -> tuple[int, list[PlanDeEstudio]]:
        builder = self._builder()
        if carrera_id is not None:
            builder.filter(PlanDeEstudio.carrera_id == carrera_id)
        total = await self.session.scalar(builder.count_stmt())
        stmt = builder.paginated(skip, limit).options(joinedload(PlanDeEstudio.carrera))
        result = await self.session.execute(stmt)
        return total or 0, list(result.scalars().all())

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
