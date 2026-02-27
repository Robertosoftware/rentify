#!/usr/bin/env bash
set -e

echo "==> Rentify devcontainer setup"

# Copy .env if not present
if [ ! -f /workspace/.env ]; then
  cp /workspace/.env.example /workspace/.env
  echo "==> .env created from .env.example"
fi

# Backend: install all deps (including dev) into project venv
echo "==> Installing backend dependencies with uv..."
cd /workspace/backend
uv sync
# Add backend venv to shell PATH
echo 'export PATH="/workspace/backend/.venv/bin:$PATH"' >> ~/.bashrc

# Alembic migrations
echo "==> Running Alembic migrations..."
uv run alembic upgrade head || echo "  (migrations skipped — run manually once DB is ready)"

# Frontend deps
echo "==> Installing frontend npm dependencies..."
cd /workspace/frontend
npm install

# Scrapers deps
echo "==> Installing scraper dependencies with uv..."
cd /workspace/scrapers
uv sync || true
echo 'export PATH="/workspace/scrapers/.venv/bin:$PATH"' >> ~/.bashrc

# Pre-commit hooks
echo "==> Installing pre-commit hooks..."
cd /workspace
pre-commit install || true

echo ""
echo "==> Setup complete!"
echo "  • Backend:  cd backend && uv run uvicorn app.main:app --reload"
echo "  • Frontend: cd frontend && npm run dev"
echo "  • Tests:    cd backend && uv run pytest"
echo "  • Claude Code: claude"
