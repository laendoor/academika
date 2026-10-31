from typing import Any


def _rows(result: Any) -> list[dict]:
    if isinstance(result, dict):
        return [{"campo": key, "valor": value} for key, value in result.items()]
    if all(isinstance(item, dict) for item in result):
        return result
    return [{"valor": item} for item in result]


def _columns(rows: list[dict]) -> list[str]:
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    return columns


def _line(cells: list[str], widths: list[int]) -> str:
    return "| " + " | ".join(cell.ljust(width) for cell, width in zip(cells, widths, strict=True)) + " |"


def render_result(result: Any) -> str:
    """Markdown: dict → campo/valor; lista de dicts → columnas; escalar → texto."""
    if not isinstance(result, (dict, list)):
        return str(result)
    rows = _rows(result)
    if not rows:
        return ""
    columns = _columns(rows)
    cells = [[str(row.get(column, "")) for column in columns] for row in rows]
    widths = [max(len(column), *(len(row[i]) for row in cells)) for i, column in enumerate(columns)]
    rule = "| " + " | ".join("-" * width for width in widths) + " |"
    return "\n".join([_line(columns, widths), rule, *(_line(row, widths) for row in cells)])
