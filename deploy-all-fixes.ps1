# Deploy All Fixes - Complete Solution
# This deploys all pending fixes in one go

Write-Host "🚀 Deploying All Fixes" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Fixes being deployed:" -ForegroundColor Yellow
Write-Host "✅ Backend URL fix (already deployed)" -ForegroundColor Green
Write-Host "✅ Persistent authentication" -ForegroundColor Green
Write-Host "✅ Report download (text format)" -ForegroundColor Green
Write-Host ""

Write-Host "📝 Adding all changes..." -ForegroundColor Yellow
git add .

Write-Host "📝 Committing..." -ForegroundColor Yellow
git commit -m "Deploy all frontend and backend fixes

Frontend Fixes:
- Persistent authentication (always use localStorage)
- Report download supports text format
- Removed Remember Me checkbox
- Better error handling and logging

Backend Fixes:
- Correct production backend URL
- All API requests will work

Configuration:
- Updated .env.production with correct backend URL

This completes all pending fixes for login, authentication, and report downloads."

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Nothing to commit or commit failed" -ForegroundColor Yellow
} else {
    Write-Host "✅ Committed" -ForegroundColor Green
}

Write-Host ""
Write-Host "📝 Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ DEPLOYED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⏰ Wait 2-3 minutes for Vercel to rebuild" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Then test:" -ForegroundColor Cyan
    Write-Host "1. Visit https://sentry-brown-xi.vercel.app" -ForegroundColor White
    Write-Host "2. Hard refresh: Ctrl+Shift+R" -ForegroundColor White
    Write-Host "3. Login (will work now!)" -ForegroundColor White
    Write-Host "4. Stay logged in across browser restarts" -ForegroundColor White
    Write-Host "5. Download reports in both JSON and Text formats" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Push failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "=====================" -ForegroundColor Cyan
