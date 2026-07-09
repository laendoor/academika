from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.log_event import LogEvent

T = TypeVar("T")


@dataclass
class LogEventContext:
    user_id: UUID
    log_session_factory: async_sessionmaker[AsyncSession]


_context: ContextVar[LogEventContext | None] = ContextVar("log_event_context", default=None)


def set_log_event_context(ctx: LogEventContext) -> None:
    _context.set(ctx)


def get_log_event_context() -> LogEventContext:
    ctx = _context.get()
    if ctx is None:
        raise RuntimeError("LogEventContext no seteado — usá set_log_event_context antes de llamar a @log_event")
    return ctx


DetailsExtractor = Callable[[Any], dict[str, Any]]


def log_event(
    action: str, details_extractor: DetailsExtractor
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    def decorator(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            result = await fn(*args, **kwargs)
            details = details_extractor(result)
            status = "error" if details.get("error") is not None else "ok"
            ctx = get_log_event_context()
            async with ctx.log_session_factory() as session:
                session.add(
                    LogEvent(
                        user_id=ctx.user_id,
                        action=action,
                        status=status,
                        details=details,
                    )
                )
                await session.commit()
            return result

        wrapper.__wrapped__ = fn  # type: ignore[attr-defined]
        return wrapper

    return decorator
