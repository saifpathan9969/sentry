# Start Updated Neural Brain Platform
# Runs backend and frontend with latest neural brain features

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NEURAL BRAIN SECURITY PLATFORM" -ForegroundColor Cyan
Write-Host "  Updated with Enhanced Features" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python virtual environment exists
if (Test-Path ".venv") {
    Write-Host "Activating Python virtual environment..." -ForegroundColor Yellow
    & .venv\Scripts\Activate.ps1
} else {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    & .venv\Scripts\Activate.ps1
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    pip install -r backend/requirements.txt
}

# Setup database
Write-Host "Setting up database..." -ForegroundColor Yellow
cd backend
python create_sqlite_tables.py
python create_production_users.py
cd ..

Write-Host ""
Write-Host "Starting Backend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; ..\\.venv\\Scripts\\Activate.ps1; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# Wait for backend to start
Start-Sleep -Seconds 5

# Check if Node.js is available
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    node --version | Out-Null
    Write-Host "Node.js: Available" -ForegroundColor Green
} catch {
    Write-Host "Node.js: Not found. Please install Node.js" -ForegroundColor Red
    exit 1
}

# Install frontend dependencies if needed
if (!(Test-Path "frontend/node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    cd frontend
    npm install
    cd ..
}

Write-Host ""
Write-Host "Starting Frontend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

# Wait for services to start
Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test connectivity
Write-Host ""
Write-Host "Testing connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    Write-Host "Backend: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "Backend: Starting up..." -ForegroundColor Yellow
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "Frontend: Ready with Neural Brain!" -ForegroundColor Green
    }
} catch {
    Write-Host "Frontend: Starting up..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "NEURAL BRAIN PLATFORM READY!" -ForegroundColor Green
Write-Host ""
Write-Host "ACCESS YOUR PLATFORM:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

Write-Host "TEST CREDENTIALS:" -ForegroundColor Cyan
Write-Host "  Enterprise: saifullahpathan49@gmail.com / sentry@779969" -ForegroundColor White
Write-Host "  Enterprise: saifullah.pathan24@sanjivani.edu.in / sentry@779969" -ForegroundColor White
Write-Host ""

Write-Host "NEURAL BRAIN TEST STEPS:" -ForegroundColor Cyan
Write-Host "  1. Visit: http://localhost:3000" -ForegroundColor White
Write-Host "  2. Register with First Name, Last Name, Email, Password" -ForegroundColor White
Write-Host "  3. Login with your credentials" -ForegroundColor White
Write-Host "  4. Go to 'New Scan' page" -ForegroundColor White
Write-Host "  5. Enter target: https://example.com" -ForegroundColor White
Write-Host "  6. Click 'Neural Interface' button" -ForegroundColor White
Write-Host "  7. Experience the 3D brain visualization!" -ForegroundColor White
Write-Host ""

Write-Host "ENHANCED FEATURES:" -ForegroundColor Cyan
Write-Host "  - Enhanced registration form with First/Last name" -ForegroundColor Green
Write-Host "  - 8 brain regions with unique colors" -ForegroundColor Green
Write-Host "  - 500+ interactive neurons with dendrites" -ForegroundColor Green
Write-Host "  - 3D mouse controls (zoom, rotate, pan)" -ForegroundColor Green
Write-Host "  - Real-time scan progress animation" -ForegroundColor Green
Write-Host "  - Vulnerability alerts with visual effects" -ForegroundColor Green
Write-Host "  - Professional HUD with metrics" -ForegroundColor Green
Write-Host ""

Write-Host "Your Neural Brain Security Platform is now running!" -ForegroundColor Green
Write-Host "Visit: http://localhost:3000 to experience the enhanced interface!" -ForegroundColor White
Write-Host ""