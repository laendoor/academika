import csv
import logging
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_csv[T](
    path: Path, parse_row: Callable[[list[str]], T], encoding: str = "utf-8", has_header: bool = True
) -> list[T]:
    rows: list[T] = []
    with open(path, encoding=encoding, newline="") as f:
        reader = csv.reader(f, delimiter=";")
        if has_header:
            next(reader)
        for i, row in enumerate(reader, start=2):
            try:
                rows.append(parse_row(row))
            except Exception as e:
                logger.warning("%s fila %d inválida: %s", path.name, i, e)
    return rows


def read_headers(path: Path) -> list[str]:
    with open(path, encoding="utf-8", newline="") as f:
        first_line = f.readline().rstrip("\r\n")
    if not first_line:
        return []
    return [c.strip().lower() for c in first_line.split(";")]
