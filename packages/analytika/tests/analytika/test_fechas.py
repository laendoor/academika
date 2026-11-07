from datetime import date

import pytest
from analytika.errors import MetricaParamError
from analytika.utils.fechas import indice_periodo, parse_year, periodo


def test_periodo_usa_la_fecha_si_esta():
    assert periodo(2021, "2C", date(2021, 7, 1)) == "2021-S1"


@pytest.mark.parametrize(("anio", "cuatrimestre"), [(2021, "1C"), (2021, "2C")])
def test_periodo_sin_fecha_usa_el_cuatrimestre_guardado(anio: int, cuatrimestre: str) -> None:
    esperado = "2021-S1" if cuatrimestre == "1C" else "2021-S2"
    assert periodo(anio, cuatrimestre, None) == esperado


def test_indice_periodo():
    assert indice_periodo("2024-S1") == 4048
    assert indice_periodo("2024-S2") - indice_periodo("2023-S2") == 2


def test_parse_year():
    assert parse_year("2018", "ingreso") == 2018


def test_parse_year_invalido():
    with pytest.raises(MetricaParamError, match="ingreso"):
        parse_year("abc", "ingreso")
