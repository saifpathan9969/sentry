# AI Pentest Brain - Demo Startup Script
# Starts Backend API + Frontend for presentation

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AI-POWERED PENETRATION TESTING BRAIN" -ForegroundColor Cyan
Write-Host "  Demo Environment Startup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Set UTF-8 encoding for emoji support
$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

Write-Host "[1/3] Starting Backend API..." -ForegroundColor Yellow
$backendProcess = Start-Process -FilePath "cmd" -ArgumentList "/c cd /d `"$PSScriptRoot\backend`" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -PassThru -WindowStyle Minimized
Start-Sleep -Seconds 2

Write-Host "[2/3] Starting Frontend..." -ForegroundColor Yellow  
$frontendProcess = Start-Process -FilePath "cmd" -ArgumentList "/c cd /d `"$PSScriptRoot\frontend`" && npm run dev" -PassThru -WindowStyle Minimized
Start-Sleep -Seconds 3

Write-Host "[3/3] Ready!" -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  DEMO ENVIRONMENT READY" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend API:    http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:       http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend:       http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "  CLI Scanner:    python ai_pentest_brain_complete.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "  Creator: saifullahpathan49@gmail.com" -ForegroundColor Yellow
Write-Host "           saifullah.pathan24@sanjivani.edu.in" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to open the demo in browser..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open browser
Start-Process "http://localhost:8000/docs"
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "Press Ctrl+C to stop all services when done." -ForegroundColor Yellow
Write-Host ""

# Wait for user to stop
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "Stopping services..." -ForegroundColor Red
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
}


