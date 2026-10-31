import clika.__main__ as entry
import pytest


def test_main_sin_database_url_sale_con_error(monkeypatch, capsys):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(SystemExit) as exc:
        entry.main()
    assert exc.value.code == 1
    assert "DATABASE_URL" in capsys.readouterr().err


def test_main_corre_el_repl(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://academika:academika@localhost:5432/academika")
    factories = []

    async def fake_run_repl(factory):
        factories.append(factory)

    monkeypatch.setattr(entry, "run_repl", fake_run_repl)
    entry.main()
    assert len(factories) == 1
