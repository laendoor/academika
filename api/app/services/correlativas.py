import uuid
from typing import Self

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.db.session import SessionDep
from app.models.correlativa import Correlativa


class CorrelativaService:
    """Lectura de correlativas (la escritura la gobierna el importador Guaraní)."""

    def __init__(self, session) -> None:
        self.session = session

    @classmethod
    def dep(cls, session: SessionDep) -> Self:
        return cls(session)

    async def list_filtered(
        self,
        skip: int = 0,
        limit: int = 20,
        materia_id: uuid.UUID | None = None,
    ) -> tuple[int, list[Correlativa]]:
        base = select(Correlativa)
        if materia_id is not None:
            base = base.where(Correlativa.materia_id == materia_id)
        total = await self.session.scalar(select(func.count()).select_from(base.subquery())) or 0
        stmt = (
            base.options(selectinload(Correlativa.materia), selectinload(Correlativa.requisito))
            .order_by(Correlativa.materia_id, Correlativa.requisito_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return total, list(result.scalars().all())
