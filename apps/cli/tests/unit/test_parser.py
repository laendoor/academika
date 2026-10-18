import pytest
from lyka.parser import Command, UsageError, parse


def test_linea_vacia_se_ignora():
    assert parse("") is None
    assert parse("   ") is None


def test_metrica_con_params():
    assert parse("metrica smoke") == Command("metrica", metric_key="smoke")
    assert parse("metrica avance limit=10 anio=2024") == Command(
        "metrica", metric_key="avance", params={"limit": "10", "anio": "2024"}
    )


def test_metrica_valores_crudos():
    # Decisión 2: sin coerción; cada métrica valida lo suyo.
    assert parse("metrica m limit=10").params == {"limit": "10"}
    assert parse("metrica m filtro=a=b").params == {"filtro": "a=b"}


def test_metricas_y_exit():
    assert parse("metricas") == Command("metricas")
    assert parse("exit") == Command("exit")


def test_help_general_y_por_comando():
    assert parse("help") == Command("help")
    assert parse("help metrica") == Command("help", topic="metrica")


def test_comando_es_case_insensitive():
    assert parse("METRICAS") == Command("metricas")


@pytest.mark.parametrize(
    "line",
    ["foo", "metrica", "metrica m limit", "metrica m =10", "metricas x", "exit x", "help a b"],
)
def test_uso_invalido_levanta_usage_error(line):
    with pytest.raises(UsageError):
        parse(line)
