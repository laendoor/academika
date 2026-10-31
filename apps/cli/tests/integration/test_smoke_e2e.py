from lyka.parser import parse
from lyka.repl import execute
from rich.table import Table


async def test_metrica_smoke_end_to_end(session_factory):
    command = parse("metrica smoke")
    assert command is not None
    output = await execute(command, session_factory)
    assert isinstance(output, Table)
    assert [column.header for column in output.columns] == ["campo", "valor"]
