import shlex
from dataclasses import dataclass, field


class UsageError(ValueError):
    """Comando mal formado; el REPL lo imprime y sigue."""


@dataclass(frozen=True)
class Command:
    name: str
    metric_key: str = ""
    params: dict[str, str] = field(default_factory=dict)
    topic: str = ""


def parse(line: str) -> Command | None:
    """Parsea una línea del REPL. Devuelve None ante línea vacía (ignorar)."""
    try:
        parts = shlex.split(line)
    except ValueError:
        raise UsageError("comillas sin cerrar") from None
    if not parts:
        return None
    name, args = parts[0].lower(), parts[1:]
    if name == "metrica":
        return _parse_metrica(args)
    if name == "metricas":
        _ensure_no_args(name, args)
        return Command(name)
    if name == "help":
        if len(args) > 1:
            raise UsageError("uso: help [comando]")
        return Command(name, topic=args[0].lower() if args else "")
    if name == "exit":
        _ensure_no_args(name, args)
        return Command(name)
    raise UsageError(f"comando desconocido: {name} (probá `help`)")


def _parse_metrica(args: list[str]) -> Command:
    if not args:
        raise UsageError("uso: metrica <nombre> [clave=valor ...]")
    params = {}
    for token in args[1:]:
        key, sep, value = token.partition("=")
        if not sep or not key:
            raise UsageError(f"parámetro inválido: {token} (uso clave=valor)")
        params[key] = value
    return Command("metrica", metric_key=args[0].lower(), params=params)


def _ensure_no_args(name: str, args: list[str]) -> None:
    if args:
        raise UsageError(f"{name} no recibe argumentos")
