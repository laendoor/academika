# Académika

Plataforma AI-first para seguimiento académico en la UNQ. Stack: FastAPI + Next.js + PostgreSQL.

## Requisitos

- Docker
- Node.js 20+
- [uv](https://docs.astral.sh/uv/)

## Quick start

```bash
make install          # instalar dependencias (api + ui)
make db-start         # levantar postgres en background
make alembic-upgrade  # aplicar migraciones
make seed             # seeds de referencia (LKPs) — correr siempre antes de seed-admin
make seed-admin       # crear el primer usuario admin (interactivo)
make dev-api          # servidor FastAPI en :8000
make dev-ui           # servidor Next.js en :3000
```

## Seeds

| Comando           | Cuándo usarlo                                        |
| ----------------- | ---------------------------------------------------- |
| `make seed`       | Siempre — LKPs de referencia, prod-safe, idempotente |
| `make seed-admin` | Primera vez en dev y en prod — crea el admin inicial |
| `make seed-dev`   | Solo local — datos de muestra para desarrollo        |

## Más comandos

```bash
make help
```
