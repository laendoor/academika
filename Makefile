.DEFAULT_GOAL := help

DB_URL ?= postgresql+asyncpg://academika:academika@localhost:5432/academika

.PHONY: help install clean docker-dev db-start db-stop dev-api dev-web check format \
        test test-api test-web test-integration test-api-cov test-web-cov alembic-current alembic-upgrade alembic-downgrade \
        alembic-check alembic-revision seed seed-dev seed-admin release

help: ## Muestra esta ayuda
	@grep -E '^## |^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk -F ':.*?## ' '/^## / {sub(/^## /, ""); printf "\n\033[1m%s\033[0m\n", $$0; next} {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

## Setup
install: ## Instala dependencias (workspace python + web)
	uv sync --all-packages --all-groups
	cd apps/web && npm install

clean: ## Limpia cachés y artefactos (apps + packages)
	cd apps/api && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find packages -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	cd apps/api && find . -type f -name "*.pyc" -delete
	find packages -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage .ruff_cache
	cd apps/web && rm -rf .next node_modules/.cache

## Docker
docker-dev: ## Levanta stack completo (api + web + postgres)
	docker compose -f compose.yaml up

db-start: ## Levanta solo postgres en background
	docker compose -f compose.yaml up postgres -d

db-stop: ## Detiene postgres
	docker compose -f compose.yaml stop postgres

## Dev local
dev-api: ## Servidor FastAPI con hot-reload
	cd apps/api && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-web: ## Servidor Next.js con hot-reload
	cd apps/web && npm run dev

## Calidad
check: ## Linter y verificación de formato (python + web)
	uv run ruff check apps/api packages && uv run ruff format --check apps/api packages
	cd apps/web && npm run lint

format: ## Formatea automáticamente (python + web)
	uv run ruff check --fix apps/api packages && uv run ruff format apps/api packages
	cd apps/web && npm run format

## Tests
test: ## Tests unitarios (python + web)
	uv run pytest apps/api/tests/unit/ packages/analytika
	cd apps/web && npm run test

test-api: ## Tests unitarios de la API
	uv run pytest apps/api/tests/unit/ packages/analytika

test-web: ## Tests unitarios del frontend (Vitest)
	cd apps/web && npm run test

test-integration: ## Tests de integración con DB real (testcontainers)
	uv run pytest apps/api/tests/integration/ -v

test-api-cov: ## Tests de la API (unit + integration) con coverage en consola
	uv run pytest apps/api/tests/unit/ apps/api/tests/integration/ packages/analytika --cov=app --cov-report=term-missing -q

test-web-cov: ## Tests del frontend con coverage en consola
	cd apps/web && npm run test -- --coverage

## Migraciones
alembic-current: ## Revisión actual de la DB
	cd apps/api && DATABASE_URL=$(DB_URL) uv run alembic current

alembic-upgrade: ## Aplica migraciones pendientes
	cd apps/api && DATABASE_URL=$(DB_URL) uv run alembic upgrade head

alembic-downgrade: ## Baja a revisión (uso: make alembic-downgrade REV=-1)
	cd apps/api && DATABASE_URL=$(DB_URL) uv run alembic downgrade $(REV)

alembic-check: ## Verifica que no hay migraciones pendientes
	cd apps/api && DATABASE_URL=$(DB_URL) uv run alembic check

alembic-revision: ## Genera migración (uso: make alembic-revision MSG="descripcion")
	cd apps/api && DATABASE_URL=$(DB_URL) uv run alembic revision --autogenerate -m "$(MSG)"

## Seeds
seed: ## Seeds de referencia (LKPs) — prod-safe, idempotente
	cd apps/api && DATABASE_URL=$(DB_URL) uv run python -m seeds.runner reference

seed-dev: ## Seeds de desarrollo (datos de muestra + admin@unq.edu.ar/admin) — solo local
	cd apps/api && DATABASE_URL=$(DB_URL) uv run python -m seeds.runner reference && \
	          DATABASE_URL=$(DB_URL) uv run python -m seeds.runner dev

seed-admin: ## Crea primer usuario admin (interactivo)
	cd apps/api && DATABASE_URL=$(DB_URL) uv run python -m seeds.create_admin

## Release
release: ## Crea release (bump version + git tag + push). Solo desde main en sync con origin/main.
	@test "$$(git branch --show-current)" = "main" || (echo "ERROR: release solo desde main (estás en $$(git branch --show-current))" >&2; exit 1)
	@git fetch origin main --quiet
	@test "$$(git rev-parse main)" = "$$(git rev-parse origin/main)" || (echo "ERROR: main no está en sync con origin/main (hacé pull/push primero)" >&2; exit 1)
	npm run release
