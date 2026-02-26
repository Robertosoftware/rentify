.PHONY: dev stop test test-backend test-frontend lint pre-commit logs migrate seed clean

dev:
	docker-compose -f docker-compose.dev.yml up -d --build

stop:
	docker-compose -f docker-compose.dev.yml down

logs:
	docker-compose -f docker-compose.dev.yml logs -f

test: test-backend test-frontend

test-backend:
	cd backend && pip install -r requirements.txt -q && pytest -q --tb=short

test-frontend:
	cd frontend && npm ci --silent && npm test

lint:
	cd backend && ruff check . && ruff format --check .
	cd frontend && npm run lint

pre-commit:
	pre-commit run --all-files

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python scripts/create_demo_user.py

clean:
	docker-compose -f docker-compose.dev.yml down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +
