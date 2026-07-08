import csv
import io
import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)


def parse_csv[T](content: str, parse_row: Callable[[list[str]], T], has_header: bool = True) -> list[T]:
    rows: list[T] = []
    reader = csv.reader(io.StringIO(content), delimiter=";")
    if has_header:
        next(reader)
    for i, row in enumerate(reader, start=2):
        try:
            rows.append(parse_row(row))
        except Exception as e:
            logger.warning("fila %d inválida: %s", i, e)
    return rows


def read_headers(content: str) -> list[str]:
    first_line = content.split("\n", 1)[0].rstrip("\r")
    if not first_line:
        return []
    return [c.strip().lower() for c in first_line.split(";")]
