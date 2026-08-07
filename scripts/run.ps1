# Run the DevPilot AI stack (backend + frontend) on Windows / PowerShell.
$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot

Write-Host "==> Starting backend on http://localhost:8000"
$backend = Start-Job -ArgumentList $ROOT {
    param($root)
    Push-Location "$root\backend"
    if (Test-Path ".venv") {
        & ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    } else {
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    }
}

Write-Host "==> Starting frontend on http://localhost:5173"
$frontend = Start-Job -ArgumentList $ROOT {
    param($root)
    Push-Location "$root\frontend"
    npm run dev
}

Write-Host "Press Ctrl+C to stop both servers."
try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    Stop-Job $backend, $frontend -ErrorAction SilentlyContinue
    Remove-Job $backend, $frontend -Force -ErrorAction SilentlyContinue
}
