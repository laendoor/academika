from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def session_factory_for(database_url: str) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(create_async_engine(database_url, echo=False), expire_on_commit=False)
