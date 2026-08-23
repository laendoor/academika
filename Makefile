.DEFAULT_GOAL := help

DB_URL ?= postgresql+asyncpg://academika:academika@localhost:5432/academika

.PHONY: help install clean docker-dev db-start db-stop dev-api dev-ui check format \
        test test-api test-ui test-integration alembic-current alembic-upgrade alembic-downgrade \
        alembic-check alembic-revision seed seed-dev seed-admin release

help: ## Muestra esta ayuda
	@grep -E '^## |^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk -F ':.*?## ' '/^## / {sub(/^## /, ""); printf "\n\033[1m%s\033[0m\n", $$0; next} {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

## Setup
install: ## Instala dependencias (api + ui)
	cd api && uv sync
	cd ui && npm install

clean: ## Limpia cachés y artefactos (api + ui)
	cd api && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	cd api && find . -type f -name "*.pyc" -delete
	cd api && rm -rf .pytest_cache htmlcov .coverage .ruff_cache
	cd ui && rm -rf .next node_modules/.cache

## Docker
docker-dev: ## Levanta stack completo (api + ui + postgres)
	docker compose -f compose.yaml up

db-start: ## Levanta solo postgres en background
	docker compose -f compose.yaml up postgres -d

db-stop: ## Detiene postgres
	docker compose -f compose.yaml stop postgres

## Dev local
dev-api: ## Servidor FastAPI con hot-reload
	cd api && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-ui: ## Servidor Next.js con hot-reload
	cd ui && npm run dev

## Calidad
check: ## Linter y verificación de formato (api + ui)
	cd api && uv run ruff check . && uv run ruff format --check .
	cd ui && npm run lint

format: ## Formatea automáticamente (api + ui)
	cd api && uv run ruff check --fix . && uv run ruff format .
	cd ui && npm run format

## Tests
test: ## Tests unitarios (api + ui)
	cd api && uv run pytest tests/unit/
	cd ui && npm run test

test-api: ## Tests unitarios de la API
	cd api && uv run pytest tests/unit/

test-ui: ## Tests unitarios de la UI (Vitest)
	cd ui && npm run test

test-integration: ## Tests de integración con DB real (testcontainers)
	cd api && uv run pytest tests/integration/ -v

## Migraciones
alembic-current: ## Revisión actual de la DB
	cd api && DATABASE_URL=$(DB_URL) uv run alembic current

alembic-upgrade: ## Aplica migraciones pendientes
	cd api && DATABASE_URL=$(DB_URL) uv run alembic upgrade head

alembic-downgrade: ## Baja a revisión (uso: make alembic-downgrade REV=-1)
	cd api && DATABASE_URL=$(DB_URL) uv run alembic downgrade $(REV)

alembic-check: ## Verifica que no hay migraciones pendientes
	cd api && DATABASE_URL=$(DB_URL) uv run alembic check

alembic-revision: ## Genera migración (uso: make alembic-revision MSG="descripcion")
	cd api && DATABASE_URL=$(DB_URL) uv run alembic revision --autogenerate -m "$(MSG)"

## Seeds
seed: ## Seeds de referencia (LKPs) — prod-safe, idempotente
	cd api && DATABASE_URL=$(DB_URL) uv run python -m seeds.runner reference

seed-dev: ## Seeds de desarrollo (datos de muestra) — solo local
	cd api && DATABASE_URL=$(DB_URL) uv run python -m seeds.runner reference && \
	          DATABASE_URL=$(DB_URL) uv run python -m seeds.runner dev

seed-admin: ## Crea primer usuario admin (interactivo)
	cd api && DATABASE_URL=$(DB_URL) uv run python -m seeds.create_admin

## Release
release: ## Crea release (bump version + git tag + push)
	npm run release
