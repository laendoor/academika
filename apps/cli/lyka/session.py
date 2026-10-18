import os

from db import session_factory_for
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class ConfigError(Exception):
    """Config local inválida; el CLI la imprime y sale sin stacktrace."""


def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise ConfigError(
            "lyka necesita DATABASE_URL "
            "(ej. export DATABASE_URL=postgresql://academika:academika@localhost:5432/academika)"
        )
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def get_session_factory(url: str | None = None) -> async_sessionmaker[AsyncSession]:
    return session_factory_for(url or database_url())
