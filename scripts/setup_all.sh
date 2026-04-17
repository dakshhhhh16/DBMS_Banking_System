#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/4] Creating virtual environment (if missing)"
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "[2/4] Installing Python dependencies"
python -m pip install -r requirements.txt

echo "[3/4] Preparing .env"
if [[ ! -f ".env" ]]; then
  cp .env.example .env
  echo "Created .env from .env.example."
fi

echo "[4/4] Initializing SQLite database"
bash scripts/setup_db.sh

echo "Setup complete."
echo "Run app with: bash scripts/run_dev.sh"
