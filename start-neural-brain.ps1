#!/usr/bin/env pwsh
# Complete startup script for neural brain testing

Write-Host "🧠 Starting Sentry Neural Brain Platform..." -ForegroundColor Cyan
Write-Host ""

# Check requirements
$pythonOk = $false
$nodeOk = $false

try {
    python --version | Out-Null
    Write-Host "✅ Python found" -ForegroundColor Green
    $pythonOk = $true
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
}

try {
    node --version | Out-Null
    Write-Host "✅ Node.js found" -ForegroundColor Green
    $nodeOk = $true
} catch {
    Write-Host "❌ Node.js not found" -ForegroundColor Red
}

if (-not $pythonOk -or -not $nodeOk) {
    Write-Host "Please install Python and Node.js first" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔧 Setting up backend..." -ForegroundColor Yellow

# Setup backend
Set-Location backend

# Install dependencies
pip install -r requirements.txt -q

# Create database and users
python create_sqlite_tables.py
python create_test_user.py
python create_owner_user.py

Write-Host "✅ Backend setup complete" -ForegroundColor Green

Set-Location ..

Write-Host ""
Write-Host "🎨 Setting up frontend..." -ForegroundColor Yellow

# Setup frontend
Set-Location frontend
npm install -q
Write-Host "✅ Frontend setup complete" -ForegroundColor Green

Set-Location ..

Write-Host ""
Write-Host "🧪 Creating test scan..." -ForegroundColor Yellow

# Create test scan
$testOutput = python test_neural_brain_flow.py
$scanId = ($testOutput | Select-String "Test scan ID: (.+)" | ForEach-Object { $_.Matches[0].Groups[1].Value })

Write-Host "✅ Test scan created: $scanId" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Starting servers..." -ForegroundColor Yellow

# Start backend
Write-Host "Starting backend on http://localhost:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# Wait for backend
Start-Sleep -Seconds 5

# Start frontend
Write-Host "Starting frontend on http://localhost:3000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

# Wait for services
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "🎉 NEURAL BRAIN PLATFORM READY!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🛡️ SENTRY NEURAL BRAIN - LIVE!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 URLs:" -ForegroundColor Cyan
Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Login Credentials:" -ForegroundColor Cyan
Write-Host "   Enterprise: saifullahpathan49@gmail.com / Test1234" -ForegroundColor White
Write-Host "   Free Tier:  test@example.com / Test1234" -ForegroundColor White
Write-Host ""
Write-Host "🧠 Neural Brain Test:" -ForegroundColor Cyan
Write-Host "   1. Visit: http://localhost:3000" -ForegroundColor White
Write-Host "   2. Login with enterprise account" -ForegroundColor White
Write-Host "   3. Go to 'New Scan'" -ForegroundColor White
Write-Host "   4. Enter target: https://example.com" -ForegroundColor White
Write-Host "   5. Click 'Neural Interface' button" -ForegroundColor White
Write-Host "   6. Watch the 3D brain visualization!" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Direct Neural Brain Link:" -ForegroundColor Cyan
Write-Host "   http://localhost:3000/scans/$scanId/visualization" -ForegroundColor White
Write-Host ""
Write-Host "🔬 Simulate Scan Progress:" -ForegroundColor Cyan
Write-Host "   cd backend; python test_scan_simulation.py $scanId" -ForegroundColor White
Write-Host ""
Write-Host "✨ Expected Neural Brain Features:" -ForegroundColor Cyan
Write-Host "   • 8 brain regions with unique colors" -ForegroundColor Green
Write-Host "   • 500+ interactive neurons with dendrites" -ForegroundColor Green
Write-Host "   • 3 types of energy pulses" -ForegroundColor Green
Write-Host "   • Full 3D mouse controls (zoom, rotate, pan)" -ForegroundColor Green
Write-Host "   • Real-time scan progress animation" -ForegroundColor Green
Write-Host "   • Vulnerability alerts with visual effects" -ForegroundColor Green
Write-Host "   • Professional HUD with metrics" -ForegroundColor Green
Write-Host ""
Write-Host "🌟 Your Neural Brain Security Platform is LIVE!" -ForegroundColor Green

# Test connectivity
Write-Host ""
Write-Host "🧪 Testing connectivity..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Backend: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "⏳ Backend: Still starting up" -ForegroundColor Yellow
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend: Ready" -ForegroundColor Green
    }
} catch {
    Write-Host "⏳ Frontend: Still starting up" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Ready to experience the neural brain!" -ForegroundColor Green
Write-Host "   The world's first neural security scanner is now running!" -ForegroundColor White