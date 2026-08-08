# ============================================================================
# DevPilot AI — Unified Build & Run Script (Windows / PowerShell)
#
# One script that goes through the ENTIRE codebase: checks prerequisites,
# installs dependencies, builds backend + frontend, runs linting and all test
# suites, seeds demo data, and finally starts the stack.
#
# Usage:
#   .\scripts\build.ps1                 # full pipeline: setup -> build -> check -> test -> seed -> run
#   .\scripts\build.ps1 -Setup          # install deps only (venv + pip + npm)
#   .\scripts\build.ps1 -Build          # produce artifacts (backend import check + frontend dist)
#   .\scripts\build.ps1 -Check          # lint + format + typecheck only
#   .\scripts\build.ps1 -Test           # unit tests only (pytest + vitest)
#   .\scripts\build.ps1 -E2E            # Playwright end-to-end tests only
#   .\scripts\build.ps1 -Seed           # seed the sample repository
#   .\scripts\build.ps1 -Run            # start backend + frontend only
#   .\scripts\build.ps1 -SkipE2E        # run everything except end-to-end tests
#   .\scripts\build.ps1 -NoRun          # run everything but do not start servers
# ============================================================================
param(
    [switch]$Setup,
    [switch]$Build,
    [switch]$Check,
    [switch]$Test,
    [switch]$E2E,
    [switch]$Seed,
    [switch]$Run,
    [switch]$SkipE2E,
    [switch]$NoRun
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
$VENV = "$ROOT\backend\.venv"
$BACKEND = "$ROOT\backend"
$FRONTEND = "$ROOT\frontend"
$BACKEND_ENV = "$BACKEND\.env"

function Log($msg)  { Write-Host "==> $msg" }
function Ok($msg)   { Write-Host "   [OK] $msg" -ForegroundColor Green }
function Die($msg)  { Write-Host "[FAIL] $msg" -ForegroundColor Red; exit 1 }

# ---- phase toggles (default: everything) ----------------------------------
$doSetup = $true; $doBuild = $true; $doCheck = $true
$doTest = $true;  $doE2E = $true;   $doSeed = $true; $doRun = $true

if ($Setup) { $doBuild = $false; $doCheck = $false; $doTest = $false; $doE2E = $false; $doSeed = $false; $doRun = $false }
if ($Build) { $doSetup = $false; $doCheck = $false; $doTest = $false; $doE2E = $false; $doSeed = $false; $doRun = $false }
if ($Check) { $doSetup = $false; $doBuild = $false; $doTest = $false; $doE2E = $false; $doSeed = $false; $doRun = $false }
if ($Test)  { $doSetup = $false; $doBuild = $false; $doCheck = $false; $doE2E = $false; $doSeed = $false; $doRun = $false }
if ($E2E)   { $doSetup = $false; $doBuild = $false; $doCheck = $false; $doTest = $false; $doSeed = $false; $doRun = $false }
if ($Seed)  { $doSetup = $false; $doBuild = $false; $doCheck = $false; $doTest = $false; $doE2E = $false; $doRun = $false }
if ($Run)   { $doSetup = $false; $doBuild = $false; $doCheck = $false; $doTest = $false; $doE2E = $false; $doSeed = $false }
if ($SkipE2E) { $doE2E = $false }
if ($NoRun)   { $doRun = $false }

$PY = "$VENV\Scripts\python.exe"
$inVenv = Test-Path $PY
function PyExec([string]$args) {
    if ($inVenv) { & $PY $args }
    else { python $args }
}

# ============================================================================
# Prerequisites
# ============================================================================
function PrereqCheck {
    Log "Checking prerequisites"
    foreach ($cmd in @("python", "node", "npm")) {
        if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
            Die "Missing required tool: $cmd"
        }
    }
    Ok "Prerequisites satisfied"
}

# ============================================================================
# 1. Setup
# ============================================================================
function PhaseSetup {
    Log "Phase 1/6 - Setup"
    if ($inVenv) {
        Ok "Using existing virtualenv at $VENV"
    } else {
        Write-Host "   Creating Python virtual environment..."
        python -m venv "$VENV"
    }
    Write-Host "   Installing backend dependencies (requirements-dev.txt)..."
    & $PY -m pip install --quiet --upgrade pip
    & $PY -m pip install --quiet -r "$BACKEND\requirements-dev.txt"
    Write-Host "   Installing frontend dependencies (npm ci)..."
    Push-Location $FRONTEND
    npm ci --silent
    Pop-Location
    if (-not (Test-Path $BACKEND_ENV)) {
        Copy-Item "$BACKEND_ENV.example" $BACKEND_ENV
        Write-Host "   Created $BACKEND_ENV from .env.example"
    }
    & $PY -m pre_commit install 2>$null | Out-Null
    Ok "Setup complete"
}

# ============================================================================
# 2. Build
# ============================================================================
function PhaseBuild {
    Log "Phase 2/6 - Build"
    if (-not $inVenv) { Die "Virtualenv missing. Run: .\scripts\build.ps1 -Setup" }
    Write-Host "   Verifying backend imports (app.main + pdf_service)..."
    Push-Location $BACKEND
    & $PY -c "import app.main; from app.services.pdf_service import PdfService; print('    backend imports OK')"
    Pop-Location
    Write-Host "   Building frontend (tsc + vite build)..."
    Push-Location $FRONTEND
    npm run build --silent
    Pop-Location
    Ok "Build complete - frontend output in frontend\dist"
}

# ============================================================================
# 3. Check
# ============================================================================
function PhaseCheck {
    Log "Phase 3/6 - Lint & typecheck"
    if (-not $inVenv) { Die "Virtualenv missing. Run: .\scripts\build.ps1 -Setup" }
    Write-Host "   ruff check (backend)..."
    Push-Location $BACKEND
    & $PY -m ruff check app tests
    Write-Host "   ruff format --check (backend)..."
    & $PY -m ruff format --check app tests
    Pop-Location
    Write-Host "   eslint (frontend)..."
    Push-Location $FRONTEND
    npm run lint --silent
    Write-Host "   tsc --noEmit (frontend)..."
    npm run typecheck --silent
    Pop-Location
    Ok "Lint & typecheck clean"
}

# ============================================================================
# 4. Test
# ============================================================================
function PhaseTest {
    Log "Phase 4/6 - Unit & integration tests"
    if (-not $inVenv) { Die "Virtualenv missing. Run: .\scripts\build.ps1 -Setup" }
    Write-Host "   pytest (backend)..."
    Push-Location $BACKEND
    & $PY -m pytest -q tests
    Pop-Location
    Write-Host "   vitest (frontend)..."
    Push-Location $FRONTEND
    npm run test --silent
    Pop-Location
    Ok "Unit tests passed"
}

# ============================================================================
# 5. E2E
# ============================================================================
function PhaseE2E {
    Log "Phase 5/6 - End-to-end tests"
    Push-Location $FRONTEND
    Write-Host "   Installing Playwright chromium browser (if missing)..."
    npx playwright install chromium 2>$null | Out-Null
    Write-Host "   Running Playwright suite... (backend + frontend auto-started by config)"
    npx playwright test
    Pop-Location
    Ok "End-to-end tests passed"
}

# ============================================================================
# 6. Seed
# ============================================================================
function PhaseSeed {
    Log "Phase 6/6 - Seeding demo data"
    if (-not $inVenv) { Die "Virtualenv missing. Run: .\scripts\build.ps1 -Setup" }
    Push-Location $ROOT
    & $PY scripts\seed.py
    Pop-Location
    Ok "Sample repository seeded"
}

# ============================================================================
# Run
# ============================================================================
function PhaseRun {
    Log "Starting DevPilot AI stack"
    $backend = Start-Job -ArgumentList $ROOT {
        param($root)
        Push-Location "$root\backend"
        if (Test-Path ".venv") {
            & ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
        } else {
            python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
        }
    }
    $frontend = Start-Job -ArgumentList $ROOT {
        param($root)
        Push-Location "$root\frontend"
        npm run dev
    }
    Write-Host "   Backend : http://localhost:8000  (API docs at /docs)"
    Write-Host "   Frontend: http://localhost:5173"
    Write-Host "   Press Ctrl+C to stop both servers."
    try {
        while ($true) { Start-Sleep -Seconds 1 }
    } finally {
        Stop-Job $backend, $frontend -ErrorAction SilentlyContinue
        Remove-Job $backend, $frontend -Force -ErrorAction SilentlyContinue
    }
}

# ============================================================================
# Main
# ============================================================================
if ($doSetup -or $doRun) { PrereqCheck }

if ($doSetup) { PhaseSetup }
if ($doBuild) { PhaseBuild }
if ($doCheck) { PhaseCheck }
if ($doTest)  { PhaseTest }
if ($doE2E)   { PhaseE2E }
if ($doSeed)  { PhaseSeed }

if ($doRun) {
    Log "All phases complete. Starting the stack."
    PhaseRun
} else {
    Log "Done. Start the stack with: .\scripts\build.ps1 -Run"
}
