# Code Conventions — Académika

Decisiones de diseño que no son inferibles del código ni detectadas por ruff/pyright.
Para decisiones de stack y arquitectura, ver ADRs en `proyecto-finisterre/decisiones/`.

---

## Componentes (frontend)

El criterio es conceptual: componentizar cuando mejora la legibilidad y la estructura del código, no mecánicamente. El fragmento merece ser componente cuando tiene nombre propio y cuando su extracción hace que el código que queda sea más fácil de leer y razonar.

La repetición es la señal práctica más confiable. Los programadores la usan como heurística para no sobrediseñar: si aparece una sola vez, la abstracción puede ser prematura; cuando aparece por segunda vez, el componente se justifica. La IA tiende a estar enfocada en la tarea puntual y puede no ver patrones entre archivos — hay que proponer candidatos activamente cuando aparezca repetición o cuando la extracción mejore claramente una página.

### Ubicación

```txt
ui/src/components/
  auth/      ← componentes de dominio (auth, recovery)
  ui/        ← primitivos sin dominio (futuro)
```

### Server vs Client components

Sin `"use client"` por defecto. Agregar solo cuando el componente necesita hooks (`useState`, `useActionState`, `useSearchParams`) o event handlers interactivos. Los componentes de presentación pura funcionan en ambos contextos sin `"use client"`.

---

## Variables de entorno

Nunca acceder a `process.env.*` (frontend) ni a `os.environ` (backend) directamente en código de negocio. Toda lectura de env vars va en un módulo central:

- **Frontend:** `ui/src/lib/constants.ts`
- **Backend:** `api/app/config.py` (pydantic-settings)

```typescript
// constants.ts
export const API_URL = process.env.API_URL ?? "http://localhost:8000";
export const IS_PRODUCTION = process.env.NODE_ENV === "production";

// En el código de negocio:
import { API_URL, IS_PRODUCTION } from "@/lib/constants";
```

Ventaja: un solo lugar para auditar qué env vars usa la app, y fácil de mockear en tests.

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

### Relationships — back_populates obligatorio

Toda `relationship()` en un modelo debe tener `back_populates` con el lado opuesto declarado.
Sin `back_populates`, SQLAlchemy puede invalidar la caché de identidad de formas inesperadas y
las relaciones inversas no son navegables.

Excepción aceptada: relationships hacia lookup tables (`lkp_*`) no tienen `back_populates`
porque las lkp no exponen colecciones de vuelta (son tablas de referencia, no entidades).

### Association tables — Table() + Column() es intencional

Las tablas de asociación M2M sin columnas extra se definen con `Table()` standalone (SA legacy API):

```python
study_plan_course = Table(
    "study_plan_course",
    Base.metadata,
    Column("plan_id", Uuid, ForeignKey("study_plan.id"), primary_key=True),
    Column("course_id", Uuid, ForeignKey("course.id"), primary_key=True),
)
```

`Table()` standalone no acepta `mapped_column()` ni `Mapped[]` — `Column()` es correcto aquí.
Si la tabla de asociación necesita columnas extra (ej. `order`, `created_at`), convertirla
a un modelo completo con `mapped_column()`.

---

## Services

Cada service es responsable de las queries sobre sus propios modelos.
Si necesita datos de otro modelo debe invocar al service correspondiente,
pero no escribir la query directamente.

### Naming de métodos de búsqueda

| Prefijo  | Retorno                     | Cuándo usarlo                                                 |
| -------- | --------------------------- | ------------------------------------------------------------- |
| `find_*` | `T \| None`                 | la ausencia es un outcome válido — el caller decide qué hacer |
| `get_*`  | `T` o lanza `NotFoundError` | la ausencia es un error del caller                            |

```python
user = await self.users.find_active_by_email(email)  # None si no existe
user = await self.users.get_by_id(user_id)           # lanza NotFoundError si no existe
```

```python
# Evitar: AuthService hace una query directa sobre la tabla de User
result = await self.session.execute(select(User).where(...))

# Correcto: AuthService recibe UserService por inyección y lo usa
user = await self.users.find_active_by_email(email)
```

### Inyección de services en services

Las dependencias entre services se declaran en el constructor e inyectan desde `dep()`.
`dep()` es el único lugar que sabe cómo construir sus dependencias.

```python
class AuthService:
    def __init__(self, session: AsyncSession, users: UserService) -> None:
        self.session = session
        self.users = users

    @classmethod
    def dep(cls, session: SessionDep, users: Annotated[UserService, Depends(UserService.dep)]) -> "AuthService":
        return cls(session, users)
```

Ventaja: el constructor es puro y testeable sin FastAPI:
`AuthService(mock_session, mock_users)`.

Para uso fuera de FastAPI (seeds, scripts): instanciar manualmente:
`AuthService(session, UserService(session))`.

---

## Estilo de código

### Ramas positivas

Preferir condiciones positivas sobre negaciones, especialmente en alternativas cortas donde se retorna
en uno u otro camino. Las negaciones (y más aún sus combinaciones con `and`/`or`) aumentan la carga
cognitiva al leer.

```python
# Preferido
if user and verify_password(password, user.hashed_password):
    return tokens
raise UnauthorizedError(...)

# Evitar
if not user or not verify_password(password, user.hashed_password):
    raise UnauthorizedError(...)
return tokens
```

### Helpers `ensure_*` para guard clauses con efectos secundarios

Cuando una validación implica un `try/except` o un `if` que lanza una excepción, extraerla a una
función `_ensure_*`. El nombre comunica la intención ("garantizar que X sea válido") sin que el lector
tenga que parsear la mecánica del error.

```python
def _ensure_payload_decoded(token: str, expected_type: str) -> dict:
    try:
        return decode_token(token, expected_type=expected_type)
    except jwt.InvalidTokenError as e:
        raise UnauthorizedError("Token inválido o expirado") from e

# En el método:
payload = _ensure_payload_decoded(token, "reset")  # flujo feliz, sin ruido
user = await self.session.get(User, uuid.UUID(payload["sub"]))
```

Aplicar cuando la alternativa inline dificulta ver el flujo principal del método.
No aplicar mecánicamente: un `if x is None: raise` de una línea no necesita helper.

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
