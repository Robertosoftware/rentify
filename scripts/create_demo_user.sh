#!/usr/bin/env bash
# Create a demo user in the local dev database.
# Usage: bash scripts/create_demo_user.sh
set -euo pipefail

cd "$(dirname "$0")/../backend"
uv run python scripts/create_demo_user.py
