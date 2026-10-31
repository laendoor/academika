from clika.parser import parse
from clika.repl import execute


async def test_metrica_smoke_end_to_end(session_factory):
    command = parse("metrica smoke")
    assert command is not None
    output = await execute(command, session_factory)
    assert "| campo | valor |" in output
    assert "True" in output
