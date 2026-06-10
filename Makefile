.PHONY: help install docker-dev db-start db-stop dev-api dev-ui check format test test-integration clean \
        alembic-current alembic-upgrade alembic-downgrade alembic-check alembic-revision \
        seed seed-dev seed-admin

DB_URL ?= postgresql+asyncpg://academika:academika@localhost:5432/academika

help:
	@echo "Académika — Comandos de desarrollo"
	@echo ""
	@echo "  make install                        - Instalar dependencias (api + ui)"
	@echo "  make docker-dev                     - Levantar stack completo con Docker (api + ui + postgres)"
	@echo "  make db-start                       - Levantar base de datos en background"
	@echo "  make db-stop                        - Detener base de datos"
	@echo "  make dev-api                        - Servidor FastAPI con hot-reload"
	@echo "  make dev-ui                         - Servidor Next.js con hot-reload"
	@echo "  make check                          - Linter y verificación de formato (api + ui)"
	@echo "  make format                         - Formatear código automáticamente (api + ui)"
	@echo "  make test                           - Tests (api + ui)"
	@echo "  make test-integration               - Tests de integración con base de datos real"
	@echo "  make clean                          - Limpiar archivos de caché (api + ui)"
	@echo ""
	@echo "  make alembic-current                - Revisión actual de la DB"
	@echo "  make alembic-upgrade                - Aplicar migraciones pendientes"
	@echo "  make alembic-downgrade REV=<rev>    - Bajar a revisión (ej: REV=-1 o REV=abc123)"
	@echo "  make alembic-check                  - Verificar que no hay migraciones pendientes"
	@echo "  make alembic-revision MSG=\"...\"     - Generar migración (NO aplica — revisar antes)
	@echo ""
	@echo "  make seed                           - Seeds de referencia (LKPs) — prod-safe, idempotente"
	@echo "  make seed-admin                     - Crear primer usuario admin (interactivo, dev y prod)"
	@echo "  make seed-dev                       - Seeds de desarrollo (datos de muestra) — solo local"

install:
	cd api && uv sync
	cd ui && npm install

docker-dev:
	docker compose -f docker-compose.dev.yml up

db-start:
	docker compose -f docker-compose.dev.yml up postgres -d

db-stop:
	docker compose -f docker-compose.dev.yml stop postgres

dev-api:
	cd api && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-ui:
	cd ui && npm run dev

check:
	cd api && uv run ruff check . && uv run ruff format --check .
	cd ui && npm run lint

format:
	cd api && uv run ruff check --fix . && uv run ruff format .
	cd ui && npm run format

test:
	cd api && uv run pytest tests/unit/
	@# cd ui && npm test  (UI tests pendientes)

# Los tests de integración usan testcontainers — levantan postgres automáticamente.
# tests/unit/    → sin infraestructura, corren offline
# tests/integration/ → requieren DB (testcontainers postgres)
test-integration:
	cd api && uv run pytest tests/integration/ -v

clean:
	cd api && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	cd api && find . -type f -name "*.pyc" -delete
	cd api && rm -rf .pytest_cache htmlcov .coverage .ruff_cache
	cd ui && rm -rf .next node_modules/.cache

alembic-current:
	cd api && DATABASE_URL=$(DB_URL) uv run alembic current

alembic-upgrade:
	cd api && DATABASE_URL=$(DB_URL) uv run alembic upgrade head

alembic-downgrade:
	cd api && DATABASE_URL=$(DB_URL) uv run alembic downgrade $(REV)

alembic-check:
	cd api && DATABASE_URL=$(DB_URL) uv run alembic check

alembic-revision:
	cd api && DATABASE_URL=$(DB_URL) uv run alembic revision --autogenerate -m "$(MSG)"

seed:
	cd api && DATABASE_URL=$(DB_URL) uv run python -m app.seeds.runner reference

seed-dev:
	cd api && DATABASE_URL=$(DB_URL) uv run python -m app.seeds.runner reference && \
	          DATABASE_URL=$(DB_URL) uv run python -m app.seeds.runner dev

seed-admin:
	cd api && DATABASE_URL=$(DB_URL) uv run python -m app.seeds.create_admin
