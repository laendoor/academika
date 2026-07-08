import logging
import os
import tempfile
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from fastapi import UploadFile

from app.db.session import SessionDep
from app.errors import BusinessError, DetectorError
from app.importers.guarani.detector import GuaraniSheetType, detect_type
from app.schemas.imports import ImportFailure, ImportResponse, ImportResult
from app.services.guarani_importer import GuaraniImporterService

logger = logging.getLogger(__name__)

# Orden de procesamiento por dependencias entre tipos:
# 1) carreras y materias (no dependen de nada)
# 2) planes (necesita carreras + materias)
# 3) correlativas (necesita materias)
# 4) alumnos (necesita carreras + planes)
# 5) historial_cursadas e inscripciones (necesitan alumnos + materias + carreras)
# Cada entrada asocia el tipo con el método del importer que lo procesa (type-safe: si renombrás
# el método sin actualizar esta lista, falla en import time, no en runtime).
_ORDER: list[tuple[GuaraniSheetType, Callable[[GuaraniImporterService, list[Path]], Awaitable[tuple[int, int]]]]] = [
    (GuaraniSheetType.CARRERAS, GuaraniImporterService.importar_carreras),
    (GuaraniSheetType.MATERIAS, GuaraniImporterService.importar_materias),
    (GuaraniSheetType.PLANES, GuaraniImporterService.importar_planes),
    (GuaraniSheetType.CORRELATIVAS, GuaraniImporterService.importar_correlativas),
    (GuaraniSheetType.ALUMNOS, GuaraniImporterService.importar_alumnos),
    (GuaraniSheetType.HISTORIAL_CURSADAS, GuaraniImporterService.importar_historial_cursadas),
    (GuaraniSheetType.INSCRIPCIONES, GuaraniImporterService.importar_inscripciones),
]


@dataclass(slots=True)
class _StagedFile:
    name: str
    path: Path


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
        paths_by_type: dict[GuaraniSheetType, list[Path]] = {}
        errors: list[ImportFailure] = []
        async with self._stage(files) as staged:
            for staged_file in staged:
                try:
                    sheet_type = detect_type(staged_file.path)
                except (DetectorError, UnicodeDecodeError, OSError) as e:
                    errors.append(ImportFailure(file=staged_file.name, error=str(e)))
                    continue
                files_by_type.setdefault(sheet_type, []).append(staged_file.name)
                paths_by_type.setdefault(sheet_type, []).append(staged_file.path)

            results = await self._process_in_order(paths_by_type, files_by_type, errors)

        return ImportResponse(results=results, errors=errors)

    async def _process_in_order(
        self,
        paths_by_type: dict[GuaraniSheetType, list[Path]],
        files_by_type: dict[GuaraniSheetType, list[str]],
        errors: list[ImportFailure],
    ) -> list[ImportResult]:
        results: list[ImportResult] = []
        for sheet_type, method_fn in _ORDER:
            paths = paths_by_type.get(sheet_type)
            if not paths:
                continue
            try:
                processed, skipped = await method_fn(self._importer, paths)
            except (UnicodeDecodeError, OSError, ValueError) as e:
                await self._importer.session.rollback()
                errors.append(ImportFailure(file=f"({sheet_type.value})", error=f"importación fallida: {e}"))
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

    @asynccontextmanager
    async def _stage(self, files: list[UploadFile]) -> AsyncIterator[list[_StagedFile]]:
        staged: list[_StagedFile] = []
        try:
            for f in files:
                suffix = Path(f.filename or "upload").suffix or ".csv"
                fd, tmp_path = tempfile.mkstemp(suffix=suffix)
                with os.fdopen(fd, "wb") as out:
                    out.write(await f.read())
                staged.append(_StagedFile(name=f.filename or "", path=Path(tmp_path)))
            yield staged
        finally:
            for s in staged:
                s.path.unlink(missing_ok=True)
