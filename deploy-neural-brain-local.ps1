# Deploy Neural Brain Security Platform Locally
# This script builds and runs the updated frontend with neural brain features

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NEURAL BRAIN SECURITY PLATFORM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker Desktop
Write-Host "Checking Docker Desktop..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✅ Docker Desktop: Running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktop: Not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🚀 Building and starting services..." -ForegroundColor Green
Write-Host ""

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null

# Build and start services
Write-Host "Building frontend with neural brain features..." -ForegroundColor Yellow
docker-compose up -d --build

# Wait for services
Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Check backend health
Write-Host ""
Write-Host "🔍 Checking services..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Backend: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Backend: Starting up..." -ForegroundColor Yellow
}

# Check frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend: Ready with Neural Brain!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Frontend: Starting up..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 NEURAL BRAIN PLATFORM DEPLOYED!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 ACCESS YOUR PLATFORM:" -ForegroundColor Cyan
Write-Host "   Frontend:  http://localhost" -ForegroundColor White
Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

Write-Host "🔑 TEST CREDENTIALS:" -ForegroundColor Cyan
Write-Host "   Enterprise: saifullahpathan49@gmail.com / Test1234" -ForegroundColor White
Write-Host "   Free Tier:  test@example.com / Test1234" -ForegroundColor White
Write-Host ""

Write-Host "🧠 NEURAL BRAIN TEST STEPS:" -ForegroundColor Cyan
Write-Host "   1. Visit: http://localhost" -ForegroundColor White
Write-Host "   2. Register with First Name, Last Name, Email, Password" -ForegroundColor White
Write-Host "   3. Login with your credentials" -ForegroundColor White
Write-Host "   4. Go to 'New Scan' page" -ForegroundColor White
Write-Host "   5. Enter target: https://example.com" -ForegroundColor White
Write-Host "   6. Click '🧠 Neural Interface' button" -ForegroundColor White
Write-Host "   7. Experience the 3D brain visualization!" -ForegroundColor White
Write-Host ""

Write-Host "✨ NEURAL BRAIN FEATURES:" -ForegroundColor Cyan
Write-Host "   - 8 brain regions with unique colors" -ForegroundColor Green
Write-Host "   - 500+ interactive neurons with dendrites" -ForegroundColor Green
Write-Host "   - 3D mouse controls (zoom, rotate, pan)" -ForegroundColor Green
Write-Host "   - Real-time scan progress animation" -ForegroundColor Green
Write-Host "   - Vulnerability alerts with visual effects" -ForegroundColor Green
Write-Host "   - Professional HUD with metrics" -ForegroundColor Green
Write-Host "   - Enhanced registration with First/Last name" -ForegroundColor Green
Write-Host ""

Write-Host "🔧 MANAGEMENT:" -ForegroundColor Cyan
Write-Host "   Stop:     docker-compose down" -ForegroundColor White
Write-Host "   Restart:  docker-compose restart" -ForegroundColor White
Write-Host "   Logs:     docker-compose logs -f" -ForegroundColor White
Write-Host ""

Write-Host "YOUR NEURAL BRAIN SECURITY PLATFORM IS READY!" -ForegroundColor Green
Write-Host "Visit: http://localhost" -ForegroundColor White
Write-Host ""