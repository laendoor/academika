import csv
import logging
from collections.abc import Callable
from datetime import date
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


def parse_date(value: str) -> date:
    return date(*reversed([int(p) for p in value.strip().split("/")]))


def or_none(value: str) -> str | None:
    stripped = value.strip()
    return stripped if stripped else None


def date_to_year_term(d: date) -> tuple[int, str]:
    term = "2C" if d.month >= 7 else "1C"
    return d.year, term
