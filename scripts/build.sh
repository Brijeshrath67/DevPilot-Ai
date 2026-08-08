#!/usr/bin/env bash
# ============================================================================
# DevPilot AI — Unified Build & Run Script
#
# One script that goes through the ENTIRE codebase: checks prerequisites,
# installs dependencies, builds backend + frontend, runs linting and all test
# suites, seeds demo data, and finally starts the stack.
#
# Usage:
#   ./scripts/build.sh                 # full pipeline: setup -> build -> check -> test -> seed -> run
#   ./scripts/build.sh --setup         # install deps only (venv + pip + npm)
#   ./scripts/build.sh --build         # produce artifacts (backend import check + frontend dist)
#   ./scripts/build.sh --check         # lint + format + typecheck only
#   ./scripts/build.sh --test          # unit tests only (pytest + vitest)
#   ./scripts/build.sh --e2e           # Playwright end-to-end tests only
#   ./scripts/build.sh --seed          # seed the sample repository
#   ./scripts/build.sh --run           # start backend + frontend only
#   ./scripts/build.sh --skip-e2e      # run everything except end-to-end tests
#   ./scripts/build.sh --no-run        # run everything but do not start servers
#   ./scripts/build.sh --help
#
# Environment overrides:
#   PYTHON_BIN=python3.12  (python executable used to create the venv)
#   SKIP_PREREQ=1          (skip the tool-version prerequisite checks)
# ============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="$ROOT/backend/.venv"
BACKEND_ENV="$ROOT/backend/.env"
FRONTEND_DIR="$ROOT/frontend"
BACKEND_DIR="$ROOT/backend"

# ---- ANSI colors -----------------------------------------------------------
C_BOLD=$'\033[1m'
C_GREEN=$'\033[32m'
C_YELLOW=$'\033[33m'
C_RED=$'\033[31m'
C_DIM=$'\033[2m'
C_RESET=$'\033[0m'

log()  { printf "%s\n" "${C_BOLD}==> $*${C_RESET}"; }
ok()   { printf "%s\n" "   ${C_GREEN}✓${C_RESET} $*"; }
warn() { printf "%s\n" "   ${C_YELLOW}!${C_RESET} $*"; }
die()  { printf "%s\n" "${C_RED}✗ $*${C_RESET}" >&2; exit 1; }

# ---- phase toggles (default: everything) ----------------------------------
DO_SETUP=1; DO_BUILD=1; DO_CHECK=1; DO_TEST=1; DO_E2E=1; DO_SEED=1; DO_RUN=1

for arg in "$@"; do
  case "$arg" in
    --setup)      DO_SETUP=1; DO_BUILD=0; DO_CHECK=0; DO_TEST=0; DO_E2E=0; DO_SEED=0; DO_RUN=0 ;;
    --build)      DO_SETUP=0; DO_BUILD=1; DO_CHECK=0; DO_TEST=0; DO_E2E=0; DO_SEED=0; DO_RUN=0 ;;
    --check)      DO_SETUP=0; DO_BUILD=0; DO_CHECK=1; DO_TEST=0; DO_E2E=0; DO_SEED=0; DO_RUN=0 ;;
    --test)       DO_SETUP=0; DO_BUILD=0; DO_CHECK=0; DO_TEST=1; DO_E2E=0; DO_SEED=0; DO_RUN=0 ;;
    --e2e)        DO_SETUP=0; DO_BUILD=0; DO_CHECK=0; DO_TEST=0; DO_E2E=1; DO_SEED=0; DO_RUN=0 ;;
    --seed)       DO_SETUP=0; DO_BUILD=0; DO_CHECK=0; DO_TEST=0; DO_E2E=0; DO_SEED=1; DO_RUN=0 ;;
    --run)        DO_SETUP=0; DO_BUILD=0; DO_CHECK=0; DO_TEST=0; DO_E2E=0; DO_SEED=0; DO_RUN=1 ;;
    --skip-e2e)   DO_E2E=0 ;;
    --no-run)     DO_RUN=0 ;;
    --help|-h)
      sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "Unknown argument: $arg (run ./scripts/build.sh --help)" ;;
  esac
done

PY="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"
ACTIVATE="$VENV_DIR/bin/activate"
if [[ ! -x "$PY" && -f "$VENV_DIR/Scripts/python.exe" ]]; then
  PY="$VENV_DIR/Scripts/python.exe"; PIP="$VENV_DIR/Scripts/pip.exe"; ACTIVATE="$VENV_DIR/Scripts/activate"
fi

in_venv() { [[ -x "$PY" ]]; }

# ============================================================================
# Prerequisites
# ============================================================================
require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    die "Missing required tool: $1. Install it first (see README prerequisites)."
  fi
}

prereq_check() {
  log "Checking prerequisites"
  require_cmd "$PYTHON_BIN"
  require_cmd node
  require_cmd npm
  PY_VER="$($PYTHON_BIN -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')"
  NODE_VER="$(node -v | sed 's/^v//')"
  printf "   python %s   node %s\n" "$C_DIM$PY_VER$C_RESET" "$C_DIM$NODE_VER$C_RESET"
  ok "Prerequisites satisfied"
}

# ============================================================================
# 1. Setup — environment, dependencies, config
# ============================================================================
phase_setup() {
  log "Phase 1/6 — Setup"
  require_cmd "$PYTHON_BIN"

  if in_venv; then
    ok "Using existing virtualenv at $VENV_DIR"
  else
    echo "   Creating Python virtual environment..."
    (cd "$BACKEND_DIR" && "$PYTHON_BIN" -m venv .venv)
  fi

  echo "   Installing backend dependencies (requirements-dev.txt)..."
  "$PIP" install --quiet --upgrade pip
  "$PIP" install --quiet -r "$BACKEND_DIR/requirements-dev.txt"

  echo "   Installing frontend dependencies (npm ci)..."
  (cd "$FRONTEND_DIR" && npm ci --silent)

  if [[ ! -f "$BACKEND_ENV" ]]; then
    cp "$BACKEND_ENV.example" "$BACKEND_ENV"
    echo "   Created $BACKEND_ENV from .env.example"
  else
    ok "$BACKEND_ENV already present"
  fi

  if command -v pre-commit >/dev/null 2>&1 || in_venv; then
    "$PY" -m pre_commit install >/dev/null 2>&1 && ok "Pre-commit hooks installed"
  fi
  ok "Setup complete"
}

# ============================================================================
# 2. Build — verify backend imports, compile frontend to dist/
# ============================================================================
phase_build() {
  log "Phase 2/6 — Build"
  [[ -x "$PY" ]] || die "Virtualenv missing. Run: ./scripts/build.sh --setup"
  echo "   Verifying backend imports (app.main + pdf_service)..."
  (cd "$BACKEND_DIR" && "$PY" -c "import app.main; from app.services.pdf_service import PdfService; print('    backend imports OK')")
  echo "   Building frontend (tsc + vite build)..."
  (cd "$FRONTEND_DIR" && npm run build --silent)
  ok "Build complete — frontend output in frontend/dist"
}

# ============================================================================
# 3. Check — lint, format, typecheck (mirrors CI)
# ============================================================================
phase_check() {
  log "Phase 3/6 — Lint & typecheck"
  [[ -x "$PY" ]] || die "Virtualenv missing. Run: ./scripts/build.sh --setup"
  echo "   ruff check (backend)..."
  (cd "$BACKEND_DIR" && "$PY" -m ruff check app tests)
  echo "   ruff format --check (backend)..."
  (cd "$BACKEND_DIR" && "$PY" -m ruff format --check app tests)
  echo "   eslint (frontend)..."
  (cd "$FRONTEND_DIR" && npm run lint --silent)
  echo "   tsc --noEmit (frontend)..."
  (cd "$FRONTEND_DIR" && npm run typecheck --silent)
  ok "Lint & typecheck clean"
}

# ============================================================================
# 4. Test — unit + integration (mirrors CI)
# ============================================================================
phase_test() {
  log "Phase 4/6 — Unit & integration tests"
  [[ -x "$PY" ]] || die "Virtualenv missing. Run: ./scripts/build.sh --setup"
  echo "   pytest (backend)..."
  (cd "$BACKEND_DIR" && "$PY" -m pytest -q tests)
  echo "   vitest (frontend)..."
  (cd "$FRONTEND_DIR" && npm run test --silent)
  ok "Unit tests passed"
}

# ============================================================================
# 5. E2E — Playwright (starts both servers automatically)
# ============================================================================
phase_e2e() {
  log "Phase 5/6 — End-to-end tests"
  echo "   Installing Playwright chromium browser (if missing)..."
  (cd "$FRONTEND_DIR" && npx playwright install chromium >/dev/null 2>&1 || true)
  echo "   Running Playwright suite... (backend + frontend auto-started by config)"
  (cd "$FRONTEND_DIR" && npx playwright test)
  ok "End-to-end tests passed"
}

# ============================================================================
# 6. Seed — load the sample repository into the database
# ============================================================================
phase_seed() {
  log "Phase 6/6 — Seeding demo data"
  [[ -x "$PY" ]] || die "Virtualenv missing. Run: ./scripts/build.sh --setup"
  (cd "$ROOT" && "$PY" scripts/seed.py)
  ok "Sample repository seeded"
}

# ============================================================================
# Run — start backend + frontend
# ============================================================================
phase_run() {
  log "Starting DevPilot AI stack"
  trap 'kill 0' EXIT
  if in_venv; then
    (cd "$BACKEND_DIR" && source "$ACTIVATE" && exec uvicorn app.main:app --host 0.0.0.0 --port 8000) &
  else
    (cd "$BACKEND_DIR" && exec "$PYTHON_BIN" -m uvicorn app.main:app --host 0.0.0.0 --port 8000) &
  fi
  (cd "$FRONTEND_DIR" && exec npm run dev) &
  echo "   Backend : http://localhost:8000  (API docs at /docs)"
  echo "   Frontend: http://localhost:5173"
  echo "   Press Ctrl+C to stop both servers."
  wait
}

# ============================================================================
# Main
# ============================================================================
if [[ "$DO_SETUP$DO_BUILD$DO_CHECK$DO_TEST$DO_E2E$DO_SEED$DO_RUN" == "0000000" ]]; then
  log "Nothing to do — see ./scripts/build.sh --help"
  exit 0
fi

[[ "$DO_SETUP" == "1" || "$DO_RUN" == "1" ]] && prereq_check

[[ "$DO_SETUP" == "1" ]] && phase_setup
[[ "$DO_BUILD" == "1" ]] && phase_build
[[ "$DO_CHECK" == "1" ]] && phase_check
[[ "$DO_TEST" == "1" ]] && phase_test
[[ "$DO_E2E" == "1" ]] && phase_e2e
[[ "$DO_SEED" == "1" ]] && phase_seed

if [[ "$DO_RUN" == "1" ]]; then
  log "All phases complete. Starting the stack."
  phase_run
else
  log "Done. Start the stack with: ./scripts/build.sh --run"
fi
