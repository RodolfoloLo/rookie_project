#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-$HOME/headlines_project}"
cd "$PROJECT_DIR"

echo "[1/5] Container status"
docker compose ps

echo "[2/5] Backend health check"
curl -fsS http://127.0.0.1:8000/ || { echo "backend direct check failed"; exit 1; }

echo "[3/5] Redis health check"
docker compose exec -T redis redis-cli ping | grep -q PONG || { echo "redis health check failed"; exit 1; }

echo "[4/5] Nginx reverse proxy check"
curl -fsS http://127.0.0.1/api/news/categories || { echo "nginx /api check failed"; exit 1; }

echo "[5/5] Frontend check"
curl -fsS http://127.0.0.1/ | head -n 5

echo "Verify passed."
