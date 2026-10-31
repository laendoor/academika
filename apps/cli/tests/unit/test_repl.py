from unittest.mock import AsyncMock, MagicMock

import pytest
from clika.parser import Command
from clika.repl import execute, run_repl


def _factory_with(session) -> MagicMock:
    context = AsyncMock()
    context.__aenter__.return_value = session
    return MagicMock(return_value=context)


async def test_exit_devuelve_none():
    assert await execute(Command("exit"), AsyncMock()) is None


async def test_metricas_lista_key_y_name():
    output = await execute(Command("metricas"), AsyncMock())
    assert output.startswith("| key")
    assert "| smoke" in output
    assert "Smoke" in output


async def test_help_en_ingles():
    output = await execute(Command("help", topic="metrica"), AsyncMock())
    assert "usage" in output


async def test_help_tema_desconocido_muestra_general():
    output = await execute(Command("help", topic="foo"), AsyncMock())
    assert "commands" in output


async def test_metrica_desconocida_no_levanta():
    output = await execute(Command("metrica", metric_key="no-existe"), AsyncMock())
    assert "desconocida" in output


async def test_metrica_smoke_corre_sin_db():
    output = await execute(Command("metrica", metric_key="smoke"), _factory_with(AsyncMock()))
    assert "| campo | valor |" in output
    assert "| ok" in output
    assert "True" in output


async def test_fallo_de_db_no_tumba_el_repl():
    factory = MagicMock(side_effect=RuntimeError("caída"))
    output = await execute(Command("metrica", metric_key="smoke"), factory)
    assert "error" in output


def _scripted_prompt(monkeypatch, lines: list[str | BaseException]) -> None:
    """Cambia el PromptSession real por uno que devuelve `lines` en orden."""
    pending = list(lines)

    class FakeSession:
        def __init__(self, **_kwargs): ...

        async def prompt_async(self, *_args, **_kwargs):
            item = pending.pop(0)
            if isinstance(item, BaseException):
                raise item
            return item

    monkeypatch.setattr("clika.repl.PromptSession", FakeSession)


async def test_run_repl_sale_con_exit(monkeypatch, capsys):
    _scripted_prompt(monkeypatch, ["exit"])
    await run_repl(AsyncMock())
    assert capsys.readouterr().out == ""


async def test_run_repl_ignora_linea_vacia(monkeypatch, capsys):
    _scripted_prompt(monkeypatch, ["", "exit"])
    await run_repl(AsyncMock())
    assert capsys.readouterr().out == ""


async def test_run_repl_reporta_error_de_uso_y_sigue(monkeypatch, capsys):
    _scripted_prompt(monkeypatch, ["metrica", "exit"])
    await run_repl(AsyncMock())
    assert "uso: metrica" in capsys.readouterr().out


async def test_run_repl_imprime_la_metrica(monkeypatch, capsys):
    _scripted_prompt(monkeypatch, ["metrica smoke", "exit"])
    await run_repl(_factory_with(AsyncMock()))
    text = capsys.readouterr().out
    assert "| ok" in text
    assert "True" in text


@pytest.mark.parametrize("salida", [EOFError(), KeyboardInterrupt()])
async def test_run_repl_corta_con_eof_o_ctrl_c(monkeypatch, salida):
    _scripted_prompt(monkeypatch, [salida])
    await run_repl(AsyncMock())


async def test_run_repl_sobrevive_a_ctrl_c_en_una_metrica(monkeypatch, capsys):
    async def fake_execute(command, _factory):
        if command.name == "exit":
            return None
        raise KeyboardInterrupt

    _scripted_prompt(monkeypatch, ["metrica smoke", "exit"])
    monkeypatch.setattr("clika.repl.execute", fake_execute)
    await run_repl(AsyncMock())
    assert "cancelado" in capsys.readouterr().out
