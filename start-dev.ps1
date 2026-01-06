# AI Pentest Brain - Development Startup Script
# This script starts both backend and frontend for local development

Write-Host "Starting AI Pentest Brain Development Environment..." -ForegroundColor Cyan

# Check if Python virtual environment exists
if (-not (Test-Path "backend\.venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    Set-Location backend
    python -m venv .venv
    Set-Location ..
}

# Start Backend
Write-Host "`nStarting Backend API on http://localhost:8000..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD\backend
    & .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt -q
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Frontend on http://localhost:3000..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD\frontend
    npm install
    npm run dev
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Development servers starting..." -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop all servers" -ForegroundColor Yellow

# Keep script running and show logs
try {
    while ($true) {
        Receive-Job -Job $backendJob -ErrorAction SilentlyContinue
        Receive-Job -Job $frontendJob -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob, $frontendJob
    Remove-Job -Job $backendJob, $frontendJob
}
