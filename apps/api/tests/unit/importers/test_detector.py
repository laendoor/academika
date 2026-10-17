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
    content = (SAMPLE_DATA / file).read_text(encoding="utf-8")
    assert detect_type(content) == expected_type


def test_detect_type_unknown_content_raises() -> None:
    with pytest.raises(DetectorError):
        detect_type("foo;bar;baz\n1;2;3\n")


def test_detect_type_empty_content_raises() -> None:
    with pytest.raises(DetectorError):
        detect_type("")
