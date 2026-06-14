#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-$HOME/headlines_project}"
IMAGE_TAG="${2:-latest}"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env"

cd "$PROJECT_DIR"

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "missing: $PROJECT_DIR/$COMPOSE_FILE"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "missing: $PROJECT_DIR/$ENV_FILE"
  echo "copy .env.example to .env and fill real values first"
  exit 1
fi

if ! grep -q '^REGISTRY_IMAGE_BACKEND=' "$ENV_FILE"; then
  echo "missing REGISTRY_IMAGE_BACKEND in $ENV_FILE"
  exit 1
fi

if ! grep -q '^REGISTRY_IMAGE_FRONTEND=' "$ENV_FILE"; then
  echo "missing REGISTRY_IMAGE_FRONTEND in $ENV_FILE"
  exit 1
fi

echo "[1/7] Set image tag: $IMAGE_TAG"
if grep -q '^IMAGE_TAG=' "$ENV_FILE"; then
  sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=${IMAGE_TAG}/" "$ENV_FILE"
else
  printf '\nIMAGE_TAG=%s\n' "$IMAGE_TAG" >> "$ENV_FILE"
fi

echo "[2/7] Validate compose config"
docker compose -f "$COMPOSE_FILE" config >/dev/null

echo "[3/7] Pull application images"
docker compose -f "$COMPOSE_FILE" pull backend frontend

echo "[4/7] Start or update stack"
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

echo "[5/7] Wait for services"
sleep 8

echo "[6/7] Show status"
docker compose -f "$COMPOSE_FILE" ps

echo "[7/7] Cleanup unused old images"
docker image prune -f

echo "Deployment done. Current image tag: $IMAGE_TAG"
