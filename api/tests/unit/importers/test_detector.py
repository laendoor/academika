from pathlib import Path

import pytest

from app.errors import DetectorError
from app.importers.guarani.detector import GuaraniSheetType, detect_type

SAMPLE_DATA = Path(__file__).parents[3] / "sample-data"


@pytest.mark.parametrize(
    ("file", "expected_type"),
    [
        ("carreras.csv", GuaraniSheetType.CARRERAS),
        ("datos_personales.csv", GuaraniSheetType.ALUMNOS),
        ("alumnos_guarani.csv", GuaraniSheetType.HISTORIAL_CURSADAS),
        ("inscripciones.csv", GuaraniSheetType.INSCRIPCIONES),
        ("materias.csv", GuaraniSheetType.MATERIAS),
        ("planes_tpi.csv", GuaraniSheetType.PLANES),
        ("planes_lds.csv", GuaraniSheetType.PLANES),
        ("requisitos_tpi.csv", GuaraniSheetType.CORRELATIVAS),
        ("requisitos_lds.csv", GuaraniSheetType.CORRELATIVAS),
    ],
)
def test_detect_type_from_sample_data(file: str, expected_type: GuaraniSheetType) -> None:
    assert detect_type(SAMPLE_DATA / file) == expected_type


def test_detect_type_unknown_file_raises(tmp_path: Path) -> None:
    p = tmp_path / "raro.csv"
    p.write_text("foo;bar;baz\n1;2;3\n", encoding="utf-8")
    with pytest.raises(DetectorError):
        detect_type(p)


def test_detect_type_empty_file_raises(tmp_path: Path) -> None:
    p = tmp_path / "vacio.csv"
    p.write_text("", encoding="utf-8")
    with pytest.raises(DetectorError):
        detect_type(p)
