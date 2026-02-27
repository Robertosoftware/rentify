.PHONY: dev stop test test-backend test-frontend lint pre-commit logs migrate seed clean install

dev:
	docker-compose -f docker-compose.dev.yml up -d --build

stop:
	docker-compose -f docker-compose.dev.yml down

logs:
	docker-compose -f docker-compose.dev.yml logs -f

install:
	cd backend && uv sync
	cd scrapers && uv sync
	cd frontend && npm ci

test: test-backend test-frontend

test-backend:
	cd backend && uv run pytest -q --tb=short

test-frontend:
	cd frontend && npm ci --silent && npm test

lint:
	cd backend && uv run ruff check . && uv run ruff format --check .
	cd frontend && npm run lint

pre-commit:
	pre-commit run --all-files

migrate:
	cd backend && uv run alembic upgrade head

seed:
	cd backend && uv run python scripts/create_demo_user.py

clean:
	docker-compose -f docker-compose.dev.yml down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +
	find . -type d -name .venv -exec rm -rf {} +
