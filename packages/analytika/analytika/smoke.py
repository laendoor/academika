from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from analytika.base import MetricaBase


class SmokeMetrica(MetricaBase):
    """Ancla del motor: verifica que el circuito métrica→DB anda."""

    key = "smoke"
    name = "Smoke"

    async def run(self, session: AsyncSession, params: dict[str, Any]) -> dict[str, Any]:
        await session.execute(text("SELECT 1"))
        return {"ok": True}
