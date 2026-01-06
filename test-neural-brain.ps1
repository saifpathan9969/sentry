#!/usr/bin/env pwsh
# Test the enhanced neural brain visualization locally

Write-Host "🧠 Testing Enhanced Neural Brain Visualization..." -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
Write-Host "🔍 Checking backend status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Backend is running: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not running. Starting backend..." -ForegroundColor Yellow
    
    # Start backend in background
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    
    Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
        Write-Host "✅ Backend started: $($response.status)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to start backend" -ForegroundColor Red
        Write-Host "Please start backend manually: cd backend; uvicorn app.main:app --reload" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "🌐 Starting frontend with neural brain..." -ForegroundColor Yellow

# Navigate to frontend and start dev server
Set-Location frontend

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "🚀 Starting development server..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🧠 NEURAL BRAIN TEST ENVIRONMENT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Test Credentials:" -ForegroundColor Cyan
Write-Host "Email:    saifullahpathan49@gmail.com" -ForegroundColor White
Write-Host "Password: Test1234" -ForegroundColor White
Write-Host ""
Write-Host "🧠 Neural Brain Test Steps:" -ForegroundColor Cyan
Write-Host "1. Login with test credentials" -ForegroundColor White
Write-Host "2. Go to 'New Scan' page" -ForegroundColor White
Write-Host "3. Enter target URL (e.g., https://example.com)" -ForegroundColor White
Write-Host "4. Click 'Neural Interface' button" -ForegroundColor White
Write-Host "5. Watch the 3D brain visualization!" -ForegroundColor White
Write-Host ""
Write-Host "✨ Expected Features:" -ForegroundColor Cyan
Write-Host "• 8 brain regions with different colors" -ForegroundColor White
Write-Host "• 500+ neurons with dendrites" -ForegroundColor White
Write-Host "• Flowing energy pulses" -ForegroundColor White
Write-Host "• Mouse controls (zoom, rotate, pan)" -ForegroundColor White
Write-Host "• Real-time scan progress" -ForegroundColor White
Write-Host "• Vulnerability alerts with red effects" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start the dev server
npm run dev

Set-Location ..