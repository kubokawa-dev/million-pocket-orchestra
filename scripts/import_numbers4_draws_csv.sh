#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 /path/to/numbers4_draws.csv"
  echo "CSV format: draw_number,draw_date,numbers"
  exit 1
fi

CSV_PATH="$1"
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

# Wait for Postgres to be ready
for _ in {1..30}; do
  if docker exec -i "${CONTAINER}" pg_isready -U "${DB_USER}" -d "${DB_NAME}" >/dev/null 2>&1; then
    break
  fi
  echo "⏳ Waiting for postgres to be ready..."
  sleep 2
done

echo "📥 Importing ${CSV_PATH} into postgres..."
docker exec -i "${CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}" <<'SQL'
CREATE TABLE IF NOT EXISTS numbers4_draws (
  draw_number INTEGER PRIMARY KEY,
  draw_date TEXT NOT NULL,
  numbers TEXT NOT NULL
);
SQL

docker exec -i "${CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}" <<'SQL'
CREATE TABLE IF NOT EXISTS numbers4_draws_import (
  draw_number INTEGER,
  draw_date TEXT,
  numbers TEXT
);
TRUNCATE numbers4_draws_import;
SQL

cat "${CSV_PATH}" | docker exec -i "${CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}" -c "\\copy numbers4_draws_import(draw_number,draw_date,numbers) FROM STDIN WITH (FORMAT csv, HEADER true)"

docker exec -i "${CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}" <<'SQL'
INSERT INTO numbers4_draws (draw_number, draw_date, numbers)
SELECT draw_number, draw_date, numbers
FROM numbers4_draws_import
ON CONFLICT (draw_number) DO UPDATE
  SET draw_date = EXCLUDED.draw_date,
      numbers = EXCLUDED.numbers;
SQL

echo "✅ Import completed"
