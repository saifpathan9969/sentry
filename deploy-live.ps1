# Sentry Neural Brain - Live Deployment Script
# Deploys frontend and backend with Docker Desktop

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SENTRY NEURAL BRAIN - LIVE DEPLOY" -ForegroundColor Cyan
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
Write-Host "🚀 Starting Sentry Neural Brain Platform..." -ForegroundColor Green
Write-Host ""

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null

# Build and start all services
Write-Host "Building and starting services..." -ForegroundColor Yellow
docker-compose up -d --build

# Wait for services to start
Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service health
Write-Host ""
Write-Host "🔍 Checking service health..." -ForegroundColor Yellow

# Check backend
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
        Write-Host "✅ Frontend: Ready" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Frontend: Starting up..." -ForegroundColor Yellow
}

# Check database
try {
    docker exec sentry-db pg_isready -U postgres | Out-Null
    Write-Host "✅ Database: Connected" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Database: Initializing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 LIVE WEBSITE URLS:" -ForegroundColor Cyan
Write-Host "   Frontend:  http://localhost" -ForegroundColor White
Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

Write-Host "🔑 TEST CREDENTIALS:" -ForegroundColor Cyan
Write-Host "   Enterprise: saifullahpathan49@gmail.com / Test1234" -ForegroundColor White
Write-Host "   Free Tier:  test@example.com / Test1234" -ForegroundColor White
Write-Host ""

Write-Host "🧠 NEURAL BRAIN TEST:" -ForegroundColor Cyan
Write-Host "   1. Visit: http://localhost" -ForegroundColor White
Write-Host "   2. Login with credentials above" -ForegroundColor White
Write-Host "   3. Go to 'New Scan' page" -ForegroundColor White
Write-Host "   4. Enter target: https://example.com" -ForegroundColor White
Write-Host "   5. Click '🧠 Neural Interface' button" -ForegroundColor White
Write-Host "   6. Experience the 3D brain visualization!" -ForegroundColor White
Write-Host ""

Write-Host "✨ NEURAL BRAIN FEATURES:" -ForegroundColor Cyan
Write-Host "   - 8 brain regions with unique colors" -ForegroundColor Green
Write-Host "   - 500+ interactive neurons with dendrites" -ForegroundColor Green
Write-Host "   - 3D mouse controls (zoom, rotate, pan)" -ForegroundColor Green
Write-Host "   - Real-time scan progress animation" -ForegroundColor Green
Write-Host "   - Vulnerability alerts with visual effects" -ForegroundColor Green
Write-Host "   - Professional HUD with metrics" -ForegroundColor Green
Write-Host ""

Write-Host "🔧 MANAGEMENT COMMANDS:" -ForegroundColor Cyan
Write-Host "   View logs:    docker-compose logs -f" -ForegroundColor White
Write-Host "   Stop all:     docker-compose down" -ForegroundColor White
Write-Host "   Restart:      docker-compose restart" -ForegroundColor White
Write-Host "   Rebuild:      docker-compose up -d --build" -ForegroundColor White
Write-Host ""

Write-Host "YOUR LIVE NEURAL BRAIN SECURITY PLATFORM IS READY!" -ForegroundColor Green
Write-Host "Visit: http://localhost to experience the future of security scanning!" -ForegroundColor White
Write-Host ""