from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

type MetricaResult = dict[str, Any] | list[dict[str, Any]]


class MetricaBase(ABC):
    """Contrato mínimo de una métrica: key, name + ejecución parametrizada."""

    key: str
    name: str

    @abstractmethod
    async def run(self, session: AsyncSession, params: dict[str, Any]) -> MetricaResult:
        """Ejecuta la métrica contra la DB y devuelve una fila o una tabla de filas."""
