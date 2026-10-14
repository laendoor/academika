from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class MetricaBase(ABC):
    """Contrato mínimo de una métrica: key, name + ejecución parametrizada."""

    key: str
    name: str

    @abstractmethod
    async def run(self, session: AsyncSession, params: dict[str, Any]) -> dict[str, Any]:
        """Ejecuta la métrica contra la DB y devuelve el resultado."""
