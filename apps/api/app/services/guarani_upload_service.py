import hashlib
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.errors import DetectorError
from app.importers.guarani.detector import GuaraniSheetType, detect_type
from app.observability.log_event import LogEventContext, log_event, set_log_event_context
from app.services.guarani_importer import GuaraniImporterService
from app.services.users import UserService
from app.session import SessionFactoryDep

logger = logging.getLogger(__name__)

_MAX_FILE_SIZE = 10 * 1024 * 1024
_PREVIEW_MAX_LINES = 6  # cabecera + 5 filas
_PREVIEW_MAX_CHARS = 8 * 1024


@dataclass
class FileOutcome:
    name: str
    sheet_type: str | None = None
    processed: int = 0
    skipped: int = 0
    error: str | None = None
    file_hash: str | None = None
    preview: list[str] | None = None
    preview_truncated: bool = False
    uploader_email: str | None = None
    skipped_sample: list[str] | None = None


def _file_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _preview_lines(content: str) -> tuple[list[str], bool]:
    """Primeras líneas crudas para el log. Sin parsing: es muestra, no dato."""
    lines = content.splitlines()
    preview = lines[:_PREVIEW_MAX_LINES]
    truncated = len(lines) > _PREVIEW_MAX_LINES
    while len(preview) > 1 and sum(len(line) for line in preview) > _PREVIEW_MAX_CHARS:
        preview.pop()
        truncated = True
    if preview and sum(len(line) for line in preview) > _PREVIEW_MAX_CHARS:
        preview[0] = preview[0][:_PREVIEW_MAX_CHARS]
        truncated = True
    return preview, truncated


def _import_details(outcome: FileOutcome) -> dict[str, Any]:
    return {
        "sheet_type": outcome.sheet_type,
        "files": [outcome.name],
        "processed": outcome.processed,
        "skipped": outcome.skipped,
        "error": outcome.error,
        "file_hash": outcome.file_hash,
        "preview": outcome.preview,
        "preview_truncated": outcome.preview_truncated,
        "uploader_email": outcome.uploader_email,
        "skipped_sample": outcome.skipped_sample,
    }


class GuaraniUploadService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_factory = session_factory

    @classmethod
    def dep(cls, session_factory: SessionFactoryDep) -> Self:
        return cls(session_factory=session_factory)

    async def process_upload(self, user_id: uuid.UUID, payloads: list[tuple[str, bytes]]) -> None:
        set_log_event_context(LogEventContext(user_id=user_id, log_session_factory=self._session_factory))
        uploader_email = await self._find_uploader_email(user_id)
        prioritized = self._sort_by_dependency(payloads)
        for name, raw in prioritized:
            await self._process_one(name, raw, uploader_email)

    async def _find_uploader_email(self, user_id: uuid.UUID) -> str | None:
        async with self._session_factory() as session:
            user = await UserService(session).find_by_id(user_id)
            return user.email if user else None

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
    async def _process_one(self, name: str, raw: bytes, uploader_email: str | None = None) -> FileOutcome:
        file_hash = _file_hash(raw)
        if len(raw) > _MAX_FILE_SIZE:
            return FileOutcome(
                name=name,
                file_hash=file_hash,
                uploader_email=uploader_email,
                error=f"archivo demasiado grande (>{_MAX_FILE_SIZE // (1024 * 1024)} MiB)",
            )

        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            return FileOutcome(
                name=name, file_hash=file_hash, uploader_email=uploader_email, error=f"encoding inválido: {e}"
            )
        preview, preview_truncated = _preview_lines(content)

        sheet_type: GuaraniSheetType | None = None
        importer = GuaraniImporterService(self._session_factory())
        try:
            sheet_type = detect_type(content)
            processed, skipped = await importer.importar(sheet_type, [content])
            await importer.session.commit()
        except DetectorError as e:
            return FileOutcome(
                name=name,
                file_hash=file_hash,
                preview=preview,
                preview_truncated=preview_truncated,
                uploader_email=uploader_email,
                error=str(e),
            )
        except (ValueError, OSError) as e:
            await importer.session.rollback()
            return FileOutcome(
                name=name,
                sheet_type=sheet_type.value if sheet_type is not None else None,
                file_hash=file_hash,
                preview=preview,
                preview_truncated=preview_truncated,
                uploader_email=uploader_email,
                error=f"importación fallida: {e}",
            )
        except Exception as e:
            logger.exception("error inesperado procesando %s", name)
            await importer.session.rollback()
            return FileOutcome(
                name=name,
                sheet_type=sheet_type.value if sheet_type is not None else None,
                file_hash=file_hash,
                preview=preview,
                preview_truncated=preview_truncated,
                uploader_email=uploader_email,
                error=f"error inesperado: {e}",
            )
        finally:
            await importer.session.close()
        return FileOutcome(
            name=name,
            sheet_type=sheet_type.value,
            processed=processed,
            skipped=skipped,
            file_hash=file_hash,
            preview=preview,
            preview_truncated=preview_truncated,
            uploader_email=uploader_email,
            skipped_sample=importer.skip_sample,
        )
