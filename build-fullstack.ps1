#!/usr/bin/env pwsh

Write-Host "🚀 Building Full-Stack Application for Render" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Build frontend
Write-Host "📦 Building Frontend..." -ForegroundColor Yellow
Set-Location frontend

# Install dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
npm install

# Update frontend environment for unified deployment
Write-Host "⚙️ Updating frontend configuration..." -ForegroundColor Yellow
Set-Location ..
"VITE_API_BASE_URL=/api/v1" | Out-File -FilePath "frontend/.env.production" -Encoding UTF8

# Build for production
Write-Host "Building React app..." -ForegroundColor Cyan
Set-Location frontend
npm run build

# Go back to root
Set-Location ..

# Create backend static directory
Write-Host "📁 Setting up backend static directory..." -ForegroundColor Yellow
if (Test-Path "backend/static") {
    Remove-Item -Recurse -Force "backend/static"
}
New-Item -ItemType Directory -Path "backend/static" -Force

# Copy frontend build to backend static
Write-Host "📋 Copying frontend build to backend..." -ForegroundColor Yellow
Copy-Item -Recurse -Force "frontend/dist/*" "backend/static/"

Write-Host ""
Write-Host "✅ Full-stack build complete!" -ForegroundColor Green
Write-Host "📁 Frontend built and copied to backend/static/" -ForegroundColor White
Write-Host "🌐 API will be available at /api/v1/*" -ForegroundColor White
Write-Host "🎨 Frontend will be served from /" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Ready for Render deployment!" -ForegroundColor Green