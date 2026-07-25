#!/usr/bin/env bash
# Runs the FastAPI backend and Vue frontend together for local dev.
# Ctrl+C stops both.
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$ROOT_DIR/safe-to-spend-api"
WEB_DIR="$ROOT_DIR/safe-to-spend-web"

# --- backend setup ---
if [ ! -d "$API_DIR/.venv" ]; then
  echo "==> Creating backend virtualenv"
  python3 -m venv "$API_DIR/.venv"
fi

# shellcheck disable=SC1091
source "$API_DIR/.venv/bin/activate"
pip install -q -r "$API_DIR/requirements.txt"

if [ ! -f "$API_DIR/.env" ]; then
  cp "$API_DIR/.env.example" "$API_DIR/.env"
fi

# --- frontend setup ---
if [ ! -d "$WEB_DIR/node_modules" ]; then
  echo "==> Installing frontend dependencies"
  (cd "$WEB_DIR" && npm install)
fi

cleanup() {
  echo
  echo "==> Stopping backend and frontend"
  kill "$API_PID" "$WEB_PID" 2>/dev/null
  wait "$API_PID" "$WEB_PID" 2>/dev/null
}
trap cleanup EXIT INT TERM

echo "==> Starting backend on http://localhost:8000"
(cd "$API_DIR" && uvicorn app.main:app --reload --port 8000) &
API_PID=$!

echo "==> Starting frontend on http://localhost:5173"
(cd "$WEB_DIR" && npm run dev) &
WEB_PID=$!

wait "$API_PID" "$WEB_PID"
