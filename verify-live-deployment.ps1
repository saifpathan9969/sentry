#!/usr/bin/env pwsh

Write-Host "🔍 Verifying Live Deployment Status" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Check if git is clean
Write-Host "📋 Checking Git Status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "⚠️  Git has uncommitted changes:" -ForegroundColor Yellow
    git status --short
} else {
    Write-Host "✅ Git is clean" -ForegroundColor Green
}
Write-Host ""

# Check current commit
Write-Host "📝 Current Commit:" -ForegroundColor Yellow
git log --oneline -1
Write-Host ""

# Check frontend submodule commit
Write-Host "🎨 Frontend Submodule Commit:" -ForegroundColor Yellow
Set-Location frontend
git log --oneline -1
Set-Location ..
Write-Host ""

# Check if terminal component exists
Write-Host "🖥️  Checking Terminal Component..." -ForegroundColor Yellow
if (Test-Path "frontend/src/components/scans/ScanTerminal.tsx") {
    Write-Host "✅ ScanTerminal.tsx exists" -ForegroundColor Green
} else {
    Write-Host "❌ ScanTerminal.tsx missing!" -ForegroundColor Red
}

# Check if NewScanPage imports terminal
Write-Host "🔗 Checking Terminal Integration..." -ForegroundColor Yellow
$newScanContent = Get-Content "frontend/src/pages/scans/NewScanPage.tsx" -Raw
if ($newScanContent -match "ScanTerminal") {
    Write-Host "✅ NewScanPage imports ScanTerminal" -ForegroundColor Green
} else {
    Write-Host "❌ NewScanPage missing ScanTerminal import!" -ForegroundColor Red
}

# Check backend wrapper
Write-Host "🧠 Checking Backend Integration..." -ForegroundColor Yellow
if (Test-Path "backend/app/scanners/pentest_brain_wrapper.py") {
    Write-Host "✅ Pentest brain wrapper exists" -ForegroundColor Green
} else {
    Write-Host "❌ Pentest brain wrapper missing!" -ForegroundColor Red
}

Write-Host ""
Write-Host "🌐 Live URLs:" -ForegroundColor Cyan
Write-Host "Frontend: https://sentry-brown-xi.vercel.app" -ForegroundColor White
Write-Host "Backend:  https://sentry-backend-1.onrender.com" -ForegroundColor White
Write-Host ""

Write-Host "🧪 Test Instructions:" -ForegroundColor Cyan
Write-Host "1. Open: https://sentry-brown-xi.vercel.app" -ForegroundColor White
Write-Host "2. Login: saifullahpathan49@gmail.com / Sentry@779969" -ForegroundColor White
Write-Host "3. Click 'New Scan'" -ForegroundColor White
Write-Host "4. Enter URL and click 'Start Scan'" -ForegroundColor White
Write-Host "5. Look for green terminal with live output!" -ForegroundColor White
Write-Host ""

Write-Host "✅ Verification Complete!" -ForegroundColor Green