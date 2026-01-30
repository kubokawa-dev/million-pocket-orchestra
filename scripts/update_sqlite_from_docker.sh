#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/home/kbkkbk/Develop/kubocchi/million-pocket"

CONTAINER="million-pocket-postgres"
DB_USER="postgres"
DB_PASS="postgres"
DB_NAME="million_pocket"

# Reuse existing container if present
if docker ps -a --format '{{.Names}}' | grep -qx "million-pocket-db-1"; then
  CONTAINER="million-pocket-db-1"
  DB_USER="user"
  DB_PASS="password"
  DB_NAME="mydb"
else
  # Ensure Postgres is up
  docker compose -f "${ROOT_DIR}/docker-compose.yml" up -d
fi

# Wait for Postgres to be healthy if healthcheck exists
if docker inspect --format='{{json .State.Health.Status}}' "${CONTAINER}" 2>/dev/null | grep -q healthy; then
  : # already healthy
else
  for _ in {1..30}; do
    if docker exec -i "${CONTAINER}" pg_isready -U "${DB_USER}" -d "${DB_NAME}" >/dev/null 2>&1; then
      break
    fi
    echo "⏳ Waiting for postgres to be ready..."
    sleep 2
  done
fi

# Sync from Postgres to local SQLite
export DATABASE_URL="postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}"
python "${ROOT_DIR}/tools/migrate_to_sqlite.py"

echo "✅ SQLite updated: ${ROOT_DIR}/lottery.db"
