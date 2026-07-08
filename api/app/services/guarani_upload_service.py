import logging
from collections.abc import Awaitable, Callable
from typing import Self

from fastapi import UploadFile

from app.db.session import SessionDep
from app.errors import BusinessError, DetectorError
from app.importers.guarani.detector import GuaraniSheetType, detect_type
from app.schemas.imports import ImportFailure, ImportResponse, ImportResult
from app.services.guarani_importer import GuaraniImporterService

logger = logging.getLogger(__name__)

# ponytail: 10 MiB hard cap. CSVs admin típicos <1 MiB. Si alguna planilla
# superó este techo, branchear a streaming + tempfile — ver M2 review PR #32.
_MAX_FILE_SIZE = 10 * 1024 * 1024

# Orden de procesamiento por dependencias entre tipos:
# 1) carreras y materias (no dependen de nada)
# 2) planes (necesita carreras + materias)
# 3) correlativas (necesita materias)
# 4) alumnos (necesita carreras + planes)
# 5) historial_cursadas e inscripciones (necesitan alumnos + materias + carreras)
# Cada entrada asocia el tipo con el método del importer (type-safe: rename sin actualizar → ImportError).
_ORDER: list[tuple[GuaraniSheetType, Callable[[GuaraniImporterService, list[str]], Awaitable[tuple[int, int]]]]] = [
    (GuaraniSheetType.CARRERAS, GuaraniImporterService.importar_carreras),
    (GuaraniSheetType.MATERIAS, GuaraniImporterService.importar_materias),
    (GuaraniSheetType.PLANES, GuaraniImporterService.importar_planes),
    (GuaraniSheetType.CORRELATIVAS, GuaraniImporterService.importar_correlativas),
    (GuaraniSheetType.ALUMNOS, GuaraniImporterService.importar_alumnos),
    (GuaraniSheetType.HISTORIAL_CURSADAS, GuaraniImporterService.importar_historial_cursadas),
    (GuaraniSheetType.INSCRIPCIONES, GuaraniImporterService.importar_inscripciones),
]


class GuaraniUploadService:
    def __init__(self, importer: GuaraniImporterService) -> None:
        self._importer = importer

    @classmethod
    def dep(cls, session: SessionDep) -> Self:
        return cls(GuaraniImporterService(session))

    async def upload(self, files: list[UploadFile]) -> ImportResponse:
        if not files:
            raise BusinessError("no se recibieron archivos")

        files_by_type: dict[GuaraniSheetType, list[str]] = {}
        contents_by_type: dict[GuaraniSheetType, list[str]] = {}
        errors: list[ImportFailure] = []

        for f in files:
            raw = await f.read()
            name = f.filename or ""
            if len(raw) > _MAX_FILE_SIZE:
                errors.append(
                    ImportFailure(
                        file=name,
                        error=f"archivo demasiado grande (>{_MAX_FILE_SIZE // (1024 * 1024)} MiB)",
                    )
                )
                continue
            try:
                content = raw.decode("utf-8")
            except UnicodeDecodeError as e:
                errors.append(ImportFailure(file=name, error=f"encoding inválido: {e}"))
                continue
            try:
                sheet_type = detect_type(content)
            except DetectorError as e:
                errors.append(ImportFailure(file=name, error=str(e)))
                continue
            files_by_type.setdefault(sheet_type, []).append(name)
            contents_by_type.setdefault(sheet_type, []).append(content)

        results = await self._process_in_order(contents_by_type, files_by_type, errors)
        return ImportResponse(results=results, errors=errors)

    async def _process_in_order(
        self,
        contents_by_type: dict[GuaraniSheetType, list[str]],
        files_by_type: dict[GuaraniSheetType, list[str]],
        errors: list[ImportFailure],
    ) -> list[ImportResult]:
        results: list[ImportResult] = []
        for sheet_type, method_fn in _ORDER:
            contents = contents_by_type.get(sheet_type)
            if not contents:
                continue
            try:
                processed, skipped = await method_fn(self._importer, contents)
            except (ValueError, OSError) as e:
                await self._importer.session.rollback()
                errors.append(
                    ImportFailure(
                        file=f"({sheet_type.value})",
                        error=f"importación fallida: {e}",
                    )
                )
                continue
            results.append(
                ImportResult(
                    type=sheet_type.value,
                    files=files_by_type[sheet_type],
                    processed=processed,
                    skipped=skipped,
                )
            )
        return results
