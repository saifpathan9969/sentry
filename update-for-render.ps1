#!/usr/bin/env pwsh
# Update GitHub repositories for Render deployment

Write-Host "🚀 Updating GitHub repositories for Render deployment..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "frontend") -or -not (Test-Path "backend")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Update frontend repository
Write-Host "`n📱 Updating frontend repository..." -ForegroundColor Yellow
Set-Location frontend

# Add all changes
git add .
git commit -m "Update API client for Render deployment with Neon PostgreSQL"
git push origin main

Write-Host "✅ Frontend repository updated successfully!" -ForegroundColor Green

# Go back to root
Set-Location ..

# Update backend repository  
Write-Host "`n🔧 Updating backend repository..." -ForegroundColor Yellow
Set-Location backend

# Add all changes
git add .
git commit -m "Add Render deployment configuration with PostgreSQL support"
git push origin main

Write-Host "✅ Backend repository updated successfully!" -ForegroundColor Green

# Go back to root
Set-Location ..

Write-Host "`n🎉 Both repositories updated successfully!" -ForegroundColor Green
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Deploy backend to Render using your sentry-backend repository" -ForegroundColor White
Write-Host "   2. Deploy frontend to Vercel using your sentry-frontend repository" -ForegroundColor White
Write-Host "   3. Follow the RENDER_DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor White
Write-Host "`n🔗 Your repositories are ready for deployment!" -ForegroundColor Green