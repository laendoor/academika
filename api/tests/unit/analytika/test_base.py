from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.analytika.base import MetricaBase


class _DummyMetrica(MetricaBase):
    key = "dummy"
    name = "Dummy"

    async def run(self, session: AsyncMock, params: dict[str, Any]) -> dict[str, Any]:
        return {"params": params}


def test_base_no_instanciable():
    with pytest.raises(TypeError):
        MetricaBase()  # type: ignore[abstract]


@pytest.mark.asyncio
async def test_subclase_minima_corre():
    metrica = _DummyMetrica()
    assert (metrica.key, metrica.name) == ("dummy", "Dummy")
    assert await metrica.run(AsyncMock(), {"a": 1}) == {"params": {"a": 1}}
