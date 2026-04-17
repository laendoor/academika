# Code Conventions — Académika

Decisiones de diseño que no son inferibles del código ni detectadas por ruff/pyright.
Para decisiones de stack y arquitectura, ver ADRs en `proyecto-finisterre/decisiones/`.

---

## Testing

### Unit vs Integration

| Carpeta              | Regla                                                                 |
| -------------------- | --------------------------------------------------------------------- |
| `tests/unit/`        | Sin infraestructura. Dependencias externas mockeadas. Corren offline. |
| `tests/integration/` | Requieren infraestructura real (DB, etc.). Usan testcontainers.       |

Si un test necesita base de datos, va en `tests/integration/`. Sin excepciones.

### Fixtures de testcontainers

Los fixtures de DB viven en `tests/integration/conftest.py`, nunca en `tests/conftest.py` raíz.
Así `pytest tests/unit/` nunca arranca un contenedor.

**Patrón NullPool** — cada test recibe su propio engine sin connection pool:

```python
@pytest_asyncio.fixture
async def db_session(db_url) -> AsyncSession:
    engine = create_async_engine(db_url, poolclass=NullPool)
    ...
    yield session
    await session.rollback()
    await engine.dispose()
```

Por qué: pytest-asyncio 1.x crea un nuevo event loop por test (function scope). Un engine con pool
guarda conexiones atadas al loop anterior → `RuntimeError: Task got Future attached to a different
loop`. NullPool elimina el pool; cada test crea y destruye su engine limpio.

### Schema en tests de integración

Se usa `Base.metadata.create_all()` en el fixture `db_url` (no `alembic upgrade head`).
Velocidad sobre fidelidad de migración en el loop local. Las migraciones se validan por separado en CI
(job `alembic-check`: upgrade → check → downgrade → upgrade).

### Async SQLAlchemy — lazy loading

Los lazy loads sincrónicos están prohibidos en contexto async (lanzan `MissingGreenlet`).
Siempre cargar relaciones explícitamente:

```python
# Leer relaciones: selectinload o joinedload
result = await session.execute(
    select(PlanDeEstudio).options(selectinload(PlanDeEstudio.materias))
)

# Escribir en M2M: insert directo a la tabla de asociación
await session.execute(insert(plan_materia).values(plan_id=..., materia_id=...))
```

---

## IDs

UUID v7 via `generate_uuid()` de `app.db.base`. Nunca `uuid_utils.uuid7()` directo.

```python
id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
```

**Por qué Python-side y no el DB:** PG16 no tiene `uuidv7()` nativo (llegó en PG17). Generarlo en
Python garantiza time-ordering sin depender de la versión del motor.

**Por qué el wrapper:** `uuid_utils.UUID.__eq__` no es compatible con `uuid.UUID` stdlib. SQLAlchemy
devuelve `uuid.UUID` después de un round-trip por la DB → las comparaciones en tests fallaban.
`generate_uuid()` convierte `uuid_utils.uuid7()` → `uuid.UUID` stdlib antes de que llegue a SQLAlchemy.

---

## Alembic

**Naming de migraciones:** `yyyy-mm-dd_hash_slug` vía `file_template` en `alembic.ini`. Ejemplo:
`2026-04-16_76410612f603_schema_inicial.py`.

**`script.py.mako`** configurado con `from collections.abc import Sequence` y union types (`|`) para
que las migraciones autogeneradas sean ruff-compliant sin intervención manual.

**Validación en CI** (job `alembic-check`):

1. `alembic upgrade head` — aplica todas las migraciones
2. `alembic check` — falla si hay cambios en los modelos sin migración correspondiente
3. `alembic downgrade base` — revierte todo
4. `alembic upgrade head` — valida que el camino completo desde cero funciona

Este flujo detecta: migraciones rotas, divergencia modelo-migración, y downgrade parcial fallido.
