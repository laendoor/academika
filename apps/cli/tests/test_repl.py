from unittest.mock import AsyncMock, MagicMock

from lyka.parser import Command
from lyka.repl import execute
from rich.table import Table
from rich.text import Text


def _factory_with(session) -> MagicMock:
    context = AsyncMock()
    context.__aenter__.return_value = session
    return MagicMock(return_value=context)


def headers(table: Table) -> list[str]:
    return [column.header for column in table.columns]


async def test_exit_devuelve_none():
    assert await execute(Command("exit"), AsyncMock()) is None


async def test_metricas_lista_key_y_name():
    output = await execute(Command("metricas"), AsyncMock())
    assert isinstance(output, Table)
    assert headers(output) == ["key", "name"]
    assert output.row_count >= 1


async def test_help_en_ingles():
    output = await execute(Command("help", topic="metrica"), AsyncMock())
    assert isinstance(output, Text)
    assert "usage" in output.plain


async def test_help_tema_desconocido_muestra_general():
    output = await execute(Command("help", topic="foo"), AsyncMock())
    assert isinstance(output, Text)
    assert "commands" in output.plain


async def test_metrica_desconocida_no_levanta():
    output = await execute(Command("metrica", metric_key="no-existe"), AsyncMock())
    assert isinstance(output, Text)
    assert "desconocida" in output.plain


async def test_metrica_smoke_corre_sin_db():
    output = await execute(Command("metrica", metric_key="smoke"), _factory_with(AsyncMock()))
    assert isinstance(output, Table)
    assert headers(output) == ["campo", "valor"]


async def test_fallo_de_db_no_tumba_el_repl():
    factory = AsyncMock(side_effect=RuntimeError("caída"))
    output = await execute(Command("metrica", metric_key="smoke"), factory)
    assert isinstance(output, Text)
    assert "error" in output.plain
