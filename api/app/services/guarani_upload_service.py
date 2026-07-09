import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.session import SessionFactoryDep
from app.errors import DetectorError
from app.importers.guarani.detector import GuaraniSheetType, detect_type
from app.services.guarani_importer import GuaraniImporterService
from app.services.log_event import LogEventContext, log_event, set_log_event_context

logger = logging.getLogger(__name__)

_MAX_FILE_SIZE = 10 * 1024 * 1024


@dataclass
class FileOutcome:
    name: str
    sheet_type: str | None = None
    processed: int = 0
    skipped: int = 0
    error: str | None = None


def _import_details(outcome: FileOutcome) -> dict[str, Any]:
    return {
        "sheet_type": outcome.sheet_type,
        "files": [outcome.name],
        "processed": outcome.processed,
        "skipped": outcome.skipped,
        "error": outcome.error,
    }


class GuaraniUploadService:
    def __init__(
        self,
        importer_factory: Callable[[], GuaraniImporterService],
        log_session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._importer_factory = importer_factory
        self._log_session_factory = log_session_factory

    @classmethod
    def dep(cls, session_factory: SessionFactoryDep) -> Self:
        def importer_factory() -> GuaraniImporterService:
            return GuaraniImporterService(session_factory())

        return cls(importer_factory=importer_factory, log_session_factory=session_factory)

    async def process_upload(self, user_id: uuid.UUID, payloads: list[tuple[str, bytes]]) -> None:
        set_log_event_context(LogEventContext(user_id=user_id, log_session_factory=self._log_session_factory))
        prioritized = self._sort_by_dependency(payloads)
        for name, raw in prioritized:
            await self._process_one(name, raw)

    def _sort_by_dependency(self, payloads: list[tuple[str, bytes]]) -> list[tuple[str, bytes]]:
        order_idx = {
            GuaraniSheetType.CARRERAS: 0,
            GuaraniSheetType.MATERIAS: 1,
            GuaraniSheetType.PLANES: 2,
            GuaraniSheetType.CORRELATIVAS: 3,
            GuaraniSheetType.ALUMNOS: 4,
            GuaraniSheetType.HISTORIAL_CURSADAS: 5,
            GuaraniSheetType.INSCRIPCIONES: 6,
        }
        fallback = len(order_idx)

        def keyf(item: tuple[str, bytes]) -> int:
            _, raw = item
            try:
                content = raw.decode("utf-8")
                return order_idx[detect_type(content)]
            except (UnicodeDecodeError, DetectorError):
                return fallback

        return sorted(payloads, key=keyf)

    @log_event(action="import_guarani", details_extractor=_import_details)
    async def _process_one(self, name: str, raw: bytes) -> FileOutcome:
        if len(raw) > _MAX_FILE_SIZE:
            return FileOutcome(
                name=name,
                error=f"archivo demasiado grande (>{_MAX_FILE_SIZE // (1024 * 1024)} MiB)",
            )

        sheet_type: GuaraniSheetType | None = None
        importer: GuaraniImporterService | None = None
        try:
            content = raw.decode("utf-8")
            sheet_type = detect_type(content)
            importer = self._importer_factory()
            processed, skipped = await importer.importar(sheet_type, [content])
            await importer.session.commit()
        except UnicodeDecodeError as e:
            return FileOutcome(name=name, error=f"encoding inválido: {e}")
        except DetectorError as e:
            return FileOutcome(name=name, error=str(e))
        except (ValueError, OSError) as e:
            if importer is not None:
                await importer.session.rollback()
            return FileOutcome(
                name=name,
                sheet_type=sheet_type.value if sheet_type is not None else None,
                error=f"importación fallida: {e}",
            )
        return FileOutcome(name=name, sheet_type=sheet_type.value, processed=processed, skipped=skipped)
