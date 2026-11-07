def nota_numerica(nota: str | None) -> int | None:
    value = (nota or "").strip()
    return int(value) if value.isdigit() else None


def promedio(notas: list[int]) -> float | None:
    return round(sum(notas) / len(notas), 2) if notas else None


def porcentaje(aprobadas: int, total: int) -> float | None:
    return round(aprobadas / total * 100, 1) if total else None
