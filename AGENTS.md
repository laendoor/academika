# Académika

Stack: FastAPI (`api/`) + Next.js (`ui/`). Ver ADR-003 para decisiones de stack.

## Convenciones de código

**[docs/CODE_CONVENTIONS.md](docs/CODE_CONVENTIONS.md)** — testing (unit vs integration, NullPool,
testcontainers), IDs (UUID v7, generate_uuid), async SQLAlchemy (selectinload, no lazy loading),
Alembic (naming, validación en CI).

## Reglas clave

- Tests que requieren DB van en `tests/integration/`, nunca en `tests/unit/`
- No usar lazy loading en async SQLAlchemy — siempre `selectinload()` o `joinedload()`
- IDs: siempre via `generate_uuid()` de `app.db.base`, nunca `uuid_utils.uuid7()` directo
