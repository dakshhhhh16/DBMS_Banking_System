#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f ".env" ]]; then
  cp .env.example .env
  echo "Created .env from .env.example. Update credentials if needed."
fi

set -a
source .env
set +a

DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME="${DB_NAME:-banking_db}"

if ! command -v mysql >/dev/null 2>&1; then
  echo "mysql CLI is not installed."
  exit 1
fi

MYSQL_ARGS=("-h" "$DB_HOST" "-P" "$DB_PORT" "-u" "$DB_USER")
if [[ -n "$DB_PASSWORD" ]]; then
  MYSQL_ARGS+=("-p$DB_PASSWORD")
fi

echo "Creating database $DB_NAME if not exists"
mysql "${MYSQL_ARGS[@]}" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

echo "Applying schema from banking_system.sql"
mysql "${MYSQL_ARGS[@]}" "$DB_NAME" < banking_system.sql

echo "Database setup complete for $DB_NAME"
