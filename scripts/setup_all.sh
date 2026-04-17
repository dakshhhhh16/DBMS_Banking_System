#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

INSTALL_MYSQL=true
for arg in "$@"; do
  if [[ "$arg" == "--skip-mysql-install" ]]; then
    INSTALL_MYSQL=false
  fi
done

echo "[1/5] Creating virtual environment (if missing)"
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "[2/5] Installing Python dependencies"
pip install -r requirements.txt

echo "[3/5] Preparing .env"
if [[ ! -f ".env" ]]; then
  cp .env.example .env
  echo "Created .env from .env.example."
fi

if ! command -v mysql >/dev/null 2>&1; then
  if [[ "$INSTALL_MYSQL" == true ]] && command -v apt >/dev/null 2>&1; then
    echo "[4/5] Installing MySQL server/client via apt (sudo required)"
    sudo apt update
    sudo DEBIAN_FRONTEND=noninteractive apt install -y mysql-server mysql-client
  else
    echo "[4/5] MySQL CLI not found."
    echo "Install MySQL and rerun this script, or run with --skip-mysql-install if already installed elsewhere."
  fi
fi

if command -v mysql >/dev/null 2>&1; then
  echo "[5/5] Initializing database"
  bash scripts/setup_db.sh
else
  echo "Skipped DB init because mysql CLI is unavailable."
fi

echo "Setup complete."
echo "Run app with: bash scripts/run_dev.sh"
