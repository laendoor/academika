from app.schemas.log_events import ImportGuaraniDetails


def test_import_guarani_details_round_trip_ok() -> None:
    details = ImportGuaraniDetails(
        sheet_type="historial_cursadas",
        files=["cursadas-2024.csv", "cursadas-2025.csv"],
        processed=5231,
        skipped=142,
    )
    restored = ImportGuaraniDetails.model_validate(details.model_dump())
    assert restored == details


def test_import_guarani_details_round_trip_error() -> None:
    details = ImportGuaraniDetails(
        sheet_type=None,
        files=["materias.csv"],
        processed=0,
        skipped=0,
        error="encoding inválido: 'utf-8' codec can't decode byte 0x91",
    )
    restored = ImportGuaraniDetails.model_validate(details.model_dump())
    assert restored == details


def test_import_guarani_details_defaults() -> None:
    details = ImportGuaraniDetails(sheet_type="alumnos", files=["alumnos.csv"])
    assert details.processed == 0
    assert details.skipped == 0
    assert details.error is None
