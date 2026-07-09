import pytest
from sqlalchemy import select

from app.db.base import generate_uuid
from app.models.log_event import LogEvent
from app.models.user import User


@pytest.mark.asyncio
async def test_log_event_persists_with_jsonb_details(db_session) -> None:
    user = User(
        id=generate_uuid(),
        email="admin@unq.edu.ar",
        hashed_password="x",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    details = {
        "sheet_type": "historial_cursadas",
        "files": ["cursadas-2024.csv"],
        "processed": 5231,
        "skipped": 142,
        "error": None,
    }
    event = LogEvent(
        id=generate_uuid(),
        user_id=user.id,
        action="import_guarani",
        status="ok",
        details=details,
    )
    db_session.add(event)
    await db_session.flush()

    fetched = (await db_session.execute(select(LogEvent).where(LogEvent.id == event.id))).scalar_one()
    assert fetched.user_id == user.id
    assert fetched.action == "import_guarani"
    assert fetched.status == "ok"
    assert fetched.details == details
    assert fetched.created_at is not None


@pytest.mark.asyncio
async def test_log_event_persists_error_with_sheet_type_null(db_session) -> None:
    user = User(
        id=generate_uuid(),
        email="admin2@unq.edu.ar",
        hashed_password="x",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    error_details = {
        "sheet_type": None,
        "files": ["malo.csv"],
        "processed": 0,
        "skipped": 0,
        "error": "encoding inválido",
    }
    event = LogEvent(
        id=generate_uuid(),
        user_id=user.id,
        action="import_guarani",
        status="error",
        details=error_details,
    )
    db_session.add(event)
    await db_session.flush()

    fetched = (await db_session.execute(select(LogEvent).where(LogEvent.id == event.id))).scalar_one()
    assert fetched.status == "error"
    assert fetched.details["sheet_type"] is None
    assert fetched.details["error"] == "encoding inválido"
