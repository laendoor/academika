import asyncio
import sys

from clika.repl import run_repl
from clika.session import ConfigError, get_session_factory


def main() -> None:
    try:
        factory = get_session_factory()
    except ConfigError as e:
        print(e, file=sys.stderr)
        raise SystemExit(1) from None
    asyncio.run(run_repl(factory))


if __name__ == "__main__":
    main()
