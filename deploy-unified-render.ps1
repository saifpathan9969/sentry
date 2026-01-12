#!/usr/bin/env pwsh

Write-Host "🚀 Deploying Unified Full-Stack App to Render" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Build the full-stack application
Write-Host "📦 Building full-stack application..." -ForegroundColor Yellow
.\build-fullstack.ps1

# Verify build
if (-not (Test-Path "backend/static/index.html")) {
    Write-Host "❌ Build failed - index.html not found in backend/static" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build verified - frontend copied to backend/static" -ForegroundColor Green

# Commit changes
Write-Host "📝 Committing changes..." -ForegroundColor Yellow
git add .
git commit -m "Deploy unified full-stack app to Render

- Frontend built and copied to backend/static/
- Backend serves both API and frontend
- Single domain deployment
- Owner accounts auto-created
- Terminal and real scanning features included"

# Push to GitHub
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Go to Render Dashboard" -ForegroundColor White
Write-Host "2. Create new Web Service" -ForegroundColor White
Write-Host "3. Connect to GitHub repo: saifpathan9969/sentry" -ForegroundColor White
Write-Host "4. Render will auto-detect render.yaml" -ForegroundColor White
Write-Host "5. Deploy and get your unified URL!" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Your app will be available at: https://[service-name].onrender.com" -ForegroundColor Green
Write-Host "🔐 Login: saifullahpathan49@gmail.com / Sentry@779969" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Features included:" -ForegroundColor Cyan
Write-Host "- ✅ Frontend and backend on same domain" -ForegroundColor White
Write-Host "- ✅ Live terminal output" -ForegroundColor White
Write-Host "- ✅ Real scanning (not mock data)" -ForegroundColor White
Write-Host "- ✅ Text reports in your format" -ForegroundColor White
Write-Host "- ✅ Owner accounts auto-created" -ForegroundColor White
Write-Host "- ✅ No CORS issues" -ForegroundColor White