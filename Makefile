.PHONY: help install docker-dev db-start db-stop dev-api dev-ui check format test test-integration clean

help:
	@echo "Académika — Comandos de desarrollo"
	@echo ""
	@echo "  make install           - Instalar dependencias (api + ui)"
	@echo "  make docker-dev        - Levantar stack completo con Docker (api + ui + postgres)"
	@echo "  make db-start          - Levantar base de datos en background"
	@echo "  make db-stop           - Detener base de datos"
	@echo "  make dev-api           - Servidor FastAPI con hot-reload"
	@echo "  make dev-ui            - Servidor Next.js con hot-reload"
	@echo "  make check             - Linter y verificación de formato (api + ui)"
	@echo "  make format            - Formatear código automáticamente (api + ui)"
	@echo "  make test              - Tests (api + ui)"
	@echo "  make test-integration  - Tests de integración con base de datos real"
	@echo "  make clean             - Limpiar archivos de caché (api + ui)"

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
	cd api && uv run pytest
	@# cd ui && npm test  (UI tests pendientes)

# Pendiente hasta ticket #2 — requiere docker-compose.test.yml + Alembic
# Cuando esté listo, el comando será:
#   docker compose -f docker-compose.test.yml -p academika_test up -d --wait
#   cd api && DATABASE_URL=postgresql+psycopg://academika:academika@localhost:5433/academika_test uv run alembic upgrade head
#   cd api && uv run pytest tests/integration; \
#     EXIT=$$?; cd ..; docker compose -f docker-compose.test.yml -p academika_test down -v; exit $$EXIT
test-integration:
	@echo "Pendiente hasta ticket #2 (modelos + Alembic + docker-compose.test.yml)"

clean:
	cd api && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	cd api && find . -type f -name "*.pyc" -delete
	cd api && rm -rf .pytest_cache htmlcov .coverage .ruff_cache
	cd ui && rm -rf .next node_modules/.cache
