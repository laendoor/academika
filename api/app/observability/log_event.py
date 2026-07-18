import logging
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.log_event import LogEvent
from app.observability.ws_manager import manager

logger = logging.getLogger(__name__)

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
        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            result = await fn(*args, **kwargs)
            details = details_extractor(result)
            status = "error" if details.get("error") is not None else "ok"
            ctx = get_log_event_context()
            try:
                async with ctx.log_session_factory() as session:
                    event = LogEvent(
                        user_id=ctx.user_id,
                        action=action,
                        status=status,
                        details=details,
                    )
                    session.add(event)
                    await session.flush()
                    await session.commit()
            except Exception:
                logger.exception("no se pudo persistir log event action=%s status=%s", action, status)
                return result

            try:
                await manager.broadcast(
                    {
                        "type": "log_event",
                        "payload": {
                            "id": str(event.id),
                            "created_at": str(event.created_at),
                            "action": action,
                            "status": status,
                            "details": details,
                        },
                    }
                )
            except Exception:
                logger.exception("ws broadcast falló para action=%s", action)
            return result

        return wrapper

    return decorator
