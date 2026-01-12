# Sentry Neural Brain - Start Script
# Starts backend and frontend servers for neural brain testing

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SENTRY NEURAL BRAIN - START SCRIPT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker Desktop is running
Write-Host "Checking Docker Desktop..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "Docker Desktop: Running" -ForegroundColor Green
} catch {
    Write-Host "Docker Desktop: Not running or not installed" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting Sentry Neural Brain Platform..." -ForegroundColor Green
Write-Host ""

# Start backend
Write-Host "1. Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# Wait a moment
Start-Sleep -Seconds 3

# Start frontend
Write-Host "2. Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "Servers are starting up..." -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

Write-Host "Test Credentials:" -ForegroundColor Cyan
Write-Host "  Enterprise: saifullahpathan49@gmail.com / Test1234" -ForegroundColor White
Write-Host "  Free Tier:  test@example.com / Test1234" -ForegroundColor White
Write-Host ""

Write-Host "Neural Brain Test Steps:" -ForegroundColor Cyan
Write-Host "  1. Visit http://localhost:3000" -ForegroundColor White
Write-Host "  2. Login with test credentials" -ForegroundColor White
Write-Host "  3. Go to 'New Scan' page" -ForegroundColor White
Write-Host "  4. Enter target: https://example.com" -ForegroundColor White
Write-Host "  5. Click 'Neural Interface' button" -ForegroundColor White
Write-Host "  6. Experience the 3D brain visualization!" -ForegroundColor White
Write-Host ""

Write-Host "Expected Neural Brain Features:" -ForegroundColor Cyan
Write-Host "  - 8 brain regions with unique colors" -ForegroundColor Green
Write-Host "  - 500+ interactive neurons with dendrites" -ForegroundColor Green
Write-Host "  - 3 types of energy pulses" -ForegroundColor Green
Write-Host "  - Full 3D mouse controls (zoom, rotate, pan)" -ForegroundColor Green
Write-Host "  - Real-time scan progress animation" -ForegroundColor Green
Write-Host "  - Vulnerability alerts with visual effects" -ForegroundColor Green
Write-Host "  - Professional HUD with metrics" -ForegroundColor Green
Write-Host ""

Write-Host "Testing connectivity..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    Write-Host "Backend Status: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "Backend: Still starting up" -ForegroundColor Yellow
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "Frontend Status: Ready" -ForegroundColor Green
    }
} catch {
    Write-Host "Frontend: Still starting up" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Ready to experience the neural brain!" -ForegroundColor Green
Write-Host "The world's first neural security scanner is now running!" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")