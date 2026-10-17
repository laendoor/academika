from collections.abc import AsyncGenerator
from typing import Annotated

from db import session_factory_for
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import settings

AsyncSessionLocal = session_factory_for(settings.database_url)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return AsyncSessionLocal


SessionDep = Annotated[AsyncSession, Depends(get_session)]
SessionFactoryDep = Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)]
