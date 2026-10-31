# Académika

Stack: FastAPI (`apps/api/`) + Next.js (`apps/web/`) + packages (`packages/`). Ver ADR-003 para decisiones de stack.

## Convenciones de código

**[docs/CODE_CONVENTIONS.md](docs/CODE_CONVENTIONS.md)** — testing (unit vs integration, NullPool,
testcontainers), IDs (UUID v7, generate_uuid), async SQLAlchemy (selectinload, no lazy loading),
Alembic (naming, validación en CI).

## Reglas clave

- Tests que requieren DB van en el `tests/integration/` de su app (`apps/api/`, `apps/cli/`), nunca en `unit/` (los de packages, en `packages/<pkg>/tests/`)
- No usar lazy loading en async SQLAlchemy — siempre `selectinload()` o `joinedload()`
- IDs: siempre via `generate_uuid()` de `db.base` (package `academika-db`), nunca `uuid_utils.uuid7()` directo
- PRs siempre vía `/aika-create-pr` (preview + confirmación antes de crear) — nunca `gh pr create` directo
- Releases solo los hace Lean (`make release`, `npx release-it`, tags, version bumps): prohibido ejecutarlos — ni con OK general, solo con confirmación explícita e independiente para el release
