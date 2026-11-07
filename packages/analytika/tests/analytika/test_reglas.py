import logging
from datetime import date

import pytest
from analytika.reglas import (
    APROBADO,
    DESAPROBADO,
    EQUIVALENCIA,
    PENDIENTE_APROBACION,
    PROMOCIONADO,
    clasificar_nota,
    periodo_cuatrimestral,
)


@pytest.mark.parametrize(
    ("nota", "clase"),
    [
        ("10", PROMOCIONADO),
        ("6", PROMOCIONADO),
        ("5", APROBADO),
        ("4", APROBADO),
        ("3", DESAPROBADO),
        ("1", DESAPROBADO),
        ("A", EQUIVALENCIA),
        ("a", EQUIVALENCIA),
        ("D", DESAPROBADO),
        ("PA", PENDIENTE_APROBACION),
        (" 7 ", PROMOCIONADO),
        (None, PENDIENTE_APROBACION),
        ("", PENDIENTE_APROBACION),
    ],
)
def test_clasificar_nota(nota: str | None, clase: str) -> None:
    assert clasificar_nota(nota) == clase


def test_nota_desconocida_loguea_y_queda_pendiente(caplog) -> None:
    with caplog.at_level(logging.ERROR):
        assert clasificar_nota("X") == PENDIENTE_APROBACION

    assert "nota desconocida 'X'" in caplog.text


@pytest.mark.parametrize(
    ("fecha", "periodo"),
    [
        (date(2020, 1, 15), "2019-S2"),
        (date(2020, 3, 31), "2019-S2"),
        (date(2020, 5, 20), "2019-S2"),
        (date(2020, 6, 1), "2020-S1"),
        (date(2020, 7, 15), "2020-S1"),
        (date(2020, 9, 30), "2020-S1"),
        (date(2020, 10, 31), "2020-S1"),
        (date(2020, 11, 1), "2020-S2"),
        (date(2020, 12, 31), "2020-S2"),
        (date(2021, 2, 18), "2020-S2"),
        (date(2021, 5, 21), "2020-S2"),
    ],
)
def test_periodo_cuatrimestral(fecha: date, periodo: str) -> None:
    assert periodo_cuatrimestral(fecha) == periodo
