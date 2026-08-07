#!/usr/bin/env bash
# Set up the DevPilot AI development environment.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Setting up DevPilot AI..."

echo "==> Creating Python virtual environment"
python3 -m venv "$ROOT/backend/.venv"
# shellcheck disable=SC1091
source "$ROOT/backend/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$ROOT/backend/requirements-dev.txt"

echo "==> Installing frontend dependencies"
(cd "$ROOT/frontend" && npm install)

echo "==> Configuring environment"
if [ ! -f "$ROOT/backend/.env" ]; then
  cp "$ROOT/backend/.env.example" "$ROOT/backend/.env"
fi

echo "==> Pre-commit hooks"
(cd "$ROOT" && pre-commit install)

echo "Done. Run ./scripts/run.sh to start the stack."
