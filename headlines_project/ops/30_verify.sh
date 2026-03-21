#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-$HOME/headlines_project}"
cd "$PROJECT_DIR"

echo "[1/4] Container status"
docker compose ps

echo "[2/4] Backend health check"
curl -fsS http://127.0.0.1:8000/ || { echo "backend direct check failed"; exit 1; }

echo "[3/4] Nginx reverse proxy check"
curl -fsS http://127.0.0.1/api/news/categories || { echo "nginx /api check failed"; exit 1; }

echo "[4/4] Frontend check"
curl -fsS http://127.0.0.1/ | head -n 5

echo "Verify passed."
