import uuid

from db.models.materia import Materia
from db.models.planes_materias import planes_materias
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PlanDeEstudioService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def materias(self, plan_id: uuid.UUID) -> list[Materia]:
        stmt = select(Materia).where(
            Materia.id.in_(select(planes_materias.c.materia_id).where(planes_materias.c.plan_id == plan_id))
        )
        return list((await self.session.execute(stmt)).scalars().all())
