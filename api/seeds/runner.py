"""Ejecuta seeds SQL de un directorio en orden alfabético.

Uso:
    python -m seeds.runner reference   ← prod-safe, idempotente
    python -m seeds.runner dev         ← solo local
"""

import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy import text

from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

SQL_DIR = Path(__file__).parent / "sql"


async def run(name: str) -> None:
    seed_dir = SQL_DIR / name
    if not seed_dir.exists():
        raise FileNotFoundError(f"seed dir not found: {seed_dir}")

    sql_files = sorted(seed_dir.glob("*.sql"))
    if not sql_files:
        logger.info("%s: no SQL files found", name)
        return

    async with AsyncSessionLocal() as session:
        for sql_file in sql_files:
            statements = [s.strip() for s in sql_file.read_text().split(";") if s.strip()]
            for stmt in statements:
                await session.execute(text(stmt))
            logger.info("  ✓ %s", sql_file.name)
        await session.commit()

    logger.info("%s seed complete (%d files)", name, len(sql_files))


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    name = sys.argv[1] if len(sys.argv) > 1 else "reference"
    await run(name)


if __name__ == "__main__":
    asyncio.run(main())
