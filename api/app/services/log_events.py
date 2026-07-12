from typing import Self

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionDep
from app.models.log_event import LogEvent


class LogEventService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @classmethod
    def dep(cls, session: SessionDep) -> Self:
        return cls(session)

    async def list_import_guarani(self, skip: int = 0, limit: int = 20) -> tuple[int, list[LogEvent]]:
        total_stmt = select(func.count()).select_from(LogEvent).where(LogEvent.action == "import_guarani")
        total = await self.session.scalar(total_stmt)
        list_stmt = (
            select(LogEvent)
            .where(LogEvent.action == "import_guarani")
            .order_by(LogEvent.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(list_stmt)
        return total or 0, list(result.scalars().all())
