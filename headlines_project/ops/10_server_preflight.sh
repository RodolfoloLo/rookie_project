#!/usr/bin/env bash
set -euo pipefail

echo "[1/6] OS info"
uname -a
lsb_release -a || true

echo "[2/6] User and sudo check"
whoami
sudo -n true 2>/dev/null && echo "sudo: ok" || echo "sudo: password may be required"

echo "[3/6] Docker check"
if command -v docker >/dev/null 2>&1; then
  docker --version
else
  echo "docker: missing"
fi

if docker compose version >/dev/null 2>&1; then
  docker compose version
else
  echo "docker compose plugin: missing"
fi

echo "[4/6] Ports check (80/443)"
ss -lntp | grep -E ':80 |:443 ' || echo "No process listening on 80/443"

echo "[5/6] Project file check"
PROJECT_DIR="${1:-$HOME/headlines_project}"
if [ ! -d "$PROJECT_DIR" ]; then
  echo "Project dir not found: $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR"
for f in docker-compose.yml backend/Dockerfile frontend/Dockerfile frontend/nginx.conf backend/database.sql backend/.env; do
  if [ -f "$f" ]; then
    echo "ok: $f"
  else
    echo "missing: $f"
    exit 1
  fi
done

echo "[6/6] Compose syntax check"
docker compose config >/dev/null
echo "compose config: ok"

echo "Preflight completed successfully."
