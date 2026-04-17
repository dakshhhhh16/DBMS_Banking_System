#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f ".env" ]]; then
  cp .env.example .env
  echo "Created .env from .env.example."
fi

set -a
source .env
set +a

DB_PATH="${DB_PATH:-instance/banking.sqlite3}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
fi

echo "Applying schema from banking_system.sql to $DB_PATH"
"$PYTHON_BIN" scripts/init_sqlite_db.py --db-path "$DB_PATH"

echo "SQLite database setup complete at $DB_PATH"
