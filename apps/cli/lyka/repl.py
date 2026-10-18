from pathlib import Path

from analytika import find_metric, list_metrics
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from lyka.parser import Command, UsageError, parse
from lyka.render import render_result

HELP = {
    "": "commands: metrica <name> [key=value ...] | metricas | help [command] | exit",
    "metrica": "usage: metrica <name> [key=value ...] — run a metric and show the result",
    "metricas": "usage: metricas — list available metrics (key + name)",
    "help": "usage: help [command] — show this help or help for one command",
    "exit": "usage: exit — leave the REPL",
}


def build_completer() -> NestedCompleter:
    metrics = {metric.key: None for metric in list_metrics()}
    topics = {"metrica": None, "metricas": None, "help": None, "exit": None}
    return NestedCompleter.from_nested_dict({"metrica": metrics, "metricas": None, "help": topics, "exit": None})


async def execute(command: Command, factory: async_sessionmaker[AsyncSession]) -> str | None:
    """Ejecuta un comando. Devuelve None si hay que salir; nunca levanta."""
    if command.name == "exit":
        return None
    if command.name == "help":
        return HELP.get(command.topic, HELP[""])
    if command.name == "metricas":
        return render_result([{"key": metric.key, "name": metric.name} for metric in list_metrics()])
    metrica = find_metric(command.metric_key)
    if metrica is None:
        return f"métrica desconocida: {command.metric_key} (probá `metricas`)"
    try:
        async with factory() as session:
            result = await metrica.run(session, dict(command.params))
    except Exception as e:
        return f"error al ejecutar '{command.metric_key}': {e}"
    return render_result(result)


async def run_repl(factory: async_sessionmaker[AsyncSession]) -> None:
    session: PromptSession[str] = PromptSession(history=FileHistory(str(Path.home() / ".lyka_history")))
    completer = build_completer()
    while True:
        try:
            line = await session.prompt_async("> ", completer=completer)
        except (EOFError, KeyboardInterrupt):
            break
        try:
            command = parse(line)
        except UsageError as e:
            print(e)
            continue
        if command is None:
            continue
        try:
            output = await execute(command, factory)
        except KeyboardInterrupt:
            print("cancelado")
            continue
        if output is None:
            break
        print(output)
