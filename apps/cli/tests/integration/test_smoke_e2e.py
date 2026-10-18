from lyka.parser import parse
from lyka.repl import execute
from lyka.session import get_session_factory
from rich.table import Table


async def test_metrica_smoke_end_to_end(db_url):
    command = parse("metrica smoke")
    assert command is not None
    output = await execute(command, get_session_factory(db_url))
    assert isinstance(output, Table)
    assert [column.header for column in output.columns] == ["campo", "valor"]
