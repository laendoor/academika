from pydantic import BaseModel


class ImportGuaraniDetails(BaseModel):
    """Details de un `log_events` con `action=import_guarani`.

    Tipado de la app — la DB guarda un dict genérico en JSONB.
    `sheet_type=None` cuando el detector no reconocía el archivo (file-level error).
    """

    sheet_type: str | None
    files: list[str]
    processed: int = 0
    skipped: int = 0
    error: str | None = None
