#!/usr/bin/env bash
# Run the DevPilot AI stack (backend + frontend).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

trap 'kill 0' EXIT

echo "==> Starting backend on http://localhost:8000"
(
  cd "$ROOT/backend"
  if [ -d ".venv" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  fi
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) &

echo "==> Starting frontend on http://localhost:5173"
(cd "$ROOT/frontend" && npm run dev) &

wait
