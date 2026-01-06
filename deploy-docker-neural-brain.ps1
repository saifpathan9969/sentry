# Deploy Neural Brain Platform with Docker
# Complete deployment with enhanced neural brain features

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NEURAL BRAIN DOCKER DEPLOYMENT" -ForegroundColor Cyan
Write-Host "  Enhanced Security Platform" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker Desktop
Write-Host "Checking Docker Desktop..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "Docker: Available" -ForegroundColor Green
} catch {
    Write-Host "Docker: Not found. Please install Docker Desktop" -ForegroundColor Red
    Write-Host "Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

try {
    docker-compose --version | Out-Null
    Write-Host "Docker Compose: Available" -ForegroundColor Green
} catch {
    Write-Host "Docker Compose: Not found. Please install Docker Compose" -ForegroundColor Red
    exit 1
}

# Check if Docker is running
Write-Host "Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "Docker daemon: Running" -ForegroundColor Green
} catch {
    Write-Host "Docker daemon: Not running. Please start Docker Desktop" -ForegroundColor Red
    exit 1
}

# Stop any existing containers
Write-Host ""
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose down --remove-orphans

# Clean up old images (optional)
Write-Host "Cleaning up old images..." -ForegroundColor Yellow
docker system prune -f

# Setup database before building
Write-Host ""
Write-Host "Setting up database..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    & .venv\Scripts\Activate.ps1
} else {
    python -m venv .venv
    & .venv\Scripts\Activate.ps1
    pip install -r backend/requirements.txt
}

# Create database with updated passwords
cd backend
python create_sqlite_tables.py
python create_production_users.py
python update_owner_passwords.py
cd ..

# Build and start containers
Write-Host ""
Write-Host "Building Docker containers..." -ForegroundColor Green
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
docker-compose build --no-cache

Write-Host ""
Write-Host "Starting Neural Brain Platform..." -ForegroundColor Green
docker-compose up -d

# Wait for services to start
Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test connectivity
Write-Host ""
Write-Host "Testing connectivity..." -ForegroundColor Yellow

# Test backend
$backendReady = $false
$attempts = 0
while (-not $backendReady -and $attempts -lt 10) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
        if ($response.status -eq "healthy") {
            Write-Host "Backend: $($response.status)" -ForegroundColor Green
            $backendReady = $true
        }
    } catch {
        Write-Host "Backend: Starting up... (attempt $($attempts + 1)/10)" -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        $attempts++
    }
}

# Test frontend
$frontendReady = $false
$attempts = 0
while (-not $frontendReady -and $attempts -lt 10) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost" -Method GET -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "Frontend: Ready with Neural Brain!" -ForegroundColor Green
            $frontendReady = $true
        }
    } catch {
        Write-Host "Frontend: Starting up... (attempt $($attempts + 1)/10)" -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        $attempts++
    }
}

# Show container status
Write-Host ""
Write-Host "Container Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "NEURAL BRAIN PLATFORM DEPLOYED!" -ForegroundColor Green
Write-Host ""
Write-Host "ACCESS YOUR PLATFORM:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

Write-Host "YOUR CREDENTIALS:" -ForegroundColor Cyan
Write-Host "  Email:     saifullahpathan49@gmail.com" -ForegroundColor White
Write-Host "  Email:     saifullah.pathan24@sanjivani.edu.in" -ForegroundColor White
Write-Host "  Password:  sentry@779969" -ForegroundColor White
Write-Host "  Tier:      Enterprise (Full Access)" -ForegroundColor White
Write-Host ""

Write-Host "NEURAL BRAIN TEST STEPS:" -ForegroundColor Cyan
Write-Host "  1. Visit: http://localhost" -ForegroundColor White
Write-Host "  2. Login with your credentials above" -ForegroundColor White
Write-Host "  3. Go to 'New Scan' page" -ForegroundColor White
Write-Host "  4. Enter target: https://example.com" -ForegroundColor White
Write-Host "  5. Click 'Neural Interface' button" -ForegroundColor White
Write-Host "  6. Experience the 3D brain visualization!" -ForegroundColor White
Write-Host ""

Write-Host "ENHANCED FEATURES:" -ForegroundColor Cyan
Write-Host "  ✅ Enhanced registration form with First/Last name" -ForegroundColor Green
Write-Host "  ✅ 8 brain regions with unique colors" -ForegroundColor Green
Write-Host "  ✅ 500+ interactive neurons with dendrites" -ForegroundColor Green
Write-Host "  ✅ 3D mouse controls (zoom, rotate, pan)" -ForegroundColor Green
Write-Host "  ✅ Real-time scan progress animation" -ForegroundColor Green
Write-Host "  ✅ Vulnerability alerts with visual effects" -ForegroundColor Green
Write-Host "  ✅ Professional HUD with metrics" -ForegroundColor Green
Write-Host "  ✅ Docker containerized deployment" -ForegroundColor Green
Write-Host ""

Write-Host "DOCKER COMMANDS:" -ForegroundColor Cyan
Write-Host "  View logs:     docker-compose logs -f" -ForegroundColor White
Write-Host "  Stop platform: docker-compose down" -ForegroundColor White
Write-Host "  Restart:       docker-compose restart" -ForegroundColor White
Write-Host "  Rebuild:       docker-compose build --no-cache" -ForegroundColor White
Write-Host ""

if ($backendReady -and $frontendReady) {
    Write-Host "🎉 SUCCESS! Your Neural Brain Security Platform is LIVE!" -ForegroundColor Green
    Write-Host "Visit: http://localhost to experience the enhanced interface!" -ForegroundColor White
} else {
    Write-Host "⚠️  Platform deployed but some services may still be starting..." -ForegroundColor Yellow
    Write-Host "Check logs with: docker-compose logs -f" -ForegroundColor White
}

Write-Host ""