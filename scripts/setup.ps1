# Set up the DevPilot AI development environment (Windows / PowerShell).
$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot

Write-Host "==> Setting up DevPilot AI..."

Write-Host "==> Creating Python virtual environment"
python -m venv "$ROOT\backend\.venv"
& "$ROOT\backend\.venv\Scripts\python.exe" -m pip install --upgrade pip
& "$ROOT\backend\.venv\Scripts\python.exe" -m pip install -r "$ROOT\backend\requirements-dev.txt"

Write-Host "==> Installing frontend dependencies"
Push-Location "$ROOT\frontend"
npm install
Pop-Location

Write-Host "==> Configuring environment"
if (-not (Test-Path "$ROOT\backend\.env")) {
    Copy-Item "$ROOT\backend\.env.example" "$ROOT\backend\.env"
}

Write-Host "==> Pre-commit hooks"
& "$ROOT\backend\.venv\Scripts\python.exe" -m pre_commit install

Write-Host "Done. Run .\scripts\run.ps1 to start the stack."
