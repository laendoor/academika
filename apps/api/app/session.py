from collections.abc import AsyncGenerator
from typing import Annotated

from db import session_factory_for
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import settings

_factory: async_sessionmaker[AsyncSession] | None = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _factory
    if _factory is None:
        _factory = session_factory_for(settings.database_url)
    return _factory


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with get_session_factory()() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
SessionFactoryDep = Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)]
