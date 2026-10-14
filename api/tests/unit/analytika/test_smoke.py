from unittest.mock import AsyncMock

import pytest

from app.analytika.smoke import SmokeMetrica


@pytest.mark.asyncio
async def test_smoke_verifica_circuito():
    session = AsyncMock()
    assert await SmokeMetrica().run(session, {}) == {"ok": True}
    session.execute.assert_awaited_once()
    assert "SELECT 1" in str(session.execute.await_args.args[0])
