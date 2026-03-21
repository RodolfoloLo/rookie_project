#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-$HOME/headlines_project}"
cd "$PROJECT_DIR"

echo "[1/5] Stop old stack (if exists)"
docker compose down || true

echo "[2/5] Build images"
docker compose build --no-cache

echo "[3/5] Start stack"
docker compose up -d

echo "[4/5] Wait for containers"
sleep 8

echo "[5/5] Show status"
docker compose ps

echo "Deployment done. Next run: bash ops/30_verify.sh"
