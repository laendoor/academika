import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.routers.planes_de_estudio import get_plan, list_planes


def _make_materia(codigo: str = "MAT1") -> MagicMock:
    materia = MagicMock()
    materia.id = uuid.uuid4()
    materia.codigo = codigo
    materia.sigla = None
    materia.nombre = f"Materia {codigo}"
    materia.creditos = 6
    materia.nucleo = "basico"
    materia.horas_semanales = 4
    materia.carga_horaria_total = 64
    return materia


def _make_plan() -> MagicMock:
    plan = MagicMock()
    plan.id = uuid.uuid4()
    plan.carrera_id = uuid.uuid4()
    plan.carrera.nombre = "TPI"
    plan.nombre = "Plan 2015"
    plan.nivel = "grado"
    plan.anio = 2015
    plan.vigente = True
    plan.created_at = datetime.now(UTC)
    plan.updated_at = datetime.now(UTC)
    plan.materias = [_make_materia("MAT2"), _make_materia("MAT1")]
    return plan


@pytest.mark.asyncio
async def test_list_planes_builds_rows_with_carrera() -> None:
    service = AsyncMock()
    plan = _make_plan()
    service.list_filtered.return_value = (1, [plan])

    result = await list_planes(service)

    assert result.total == 1
    assert result.items[0].carrera_nombre == "TPI"
    assert result.items[0].anio == 2015
    service.list_filtered.assert_awaited_once_with(skip=0, limit=20, carrera_id=None)


@pytest.mark.asyncio
async def test_get_plan_builds_detail_sorted_by_nombre() -> None:
    service = AsyncMock()
    plan = _make_plan()
    service.get_detail.return_value = plan

    result = await get_plan(plan.id, service)

    assert result.carrera_nombre == "TPI"
    assert [m.codigo for m in result.materias] == ["MAT1", "MAT2"]
    service.get_detail.assert_awaited_once_with(plan.id)
