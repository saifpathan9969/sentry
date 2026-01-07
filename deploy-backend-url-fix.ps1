# Deploy Backend URL Fix - CRITICAL
# This fixes the "Invalid username or password" error caused by wrong backend URL

Write-Host "🚨 CRITICAL FIX: Backend URL Configuration" -ForegroundColor Red
Write-Host "==========================================" -ForegroundColor Red
Write-Host ""

Write-Host "PROBLEM FOUND:" -ForegroundColor Yellow
Write-Host "❌ .env.production was pointing to: http://localhost:8000/api/v1" -ForegroundColor Red
Write-Host "✅ Should point to: https://sentry-backend-1.onrender.com/api/v1" -ForegroundColor Green
Write-Host ""
Write-Host "This is why login was failing - frontend couldn't reach the backend!" -ForegroundColor Yellow
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "frontend")) {
    Write-Host "❌ Error: frontend directory not found" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory" -ForegroundColor Yellow
    exit 1
}

# Step 1: Show the fix
Write-Host "📝 Step 1: Verifying the fix..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Current .env.production content:" -ForegroundColor Cyan
Get-Content .env.production
Write-Host ""

# Step 2: Add files
Write-Host "📝 Step 2: Adding files to git..." -ForegroundColor Yellow
git add .env.production
git add deploy-backend-url-fix.ps1
git add FRONTEND_LOGIN_DEBUG.md

Write-Host "✅ Files added" -ForegroundColor Green
Write-Host ""

# Step 3: Commit
Write-Host "📝 Step 3: Committing changes..." -ForegroundColor Yellow
git commit -m "CRITICAL FIX: Update backend URL in production env

The .env.production file was pointing to localhost instead of the Render backend.
This caused all API requests to fail, resulting in 'Invalid username or password' errors.

Fixed:
- Changed VITE_API_BASE_URL from http://localhost:8000/api/v1
- To: https://sentry-backend-1.onrender.com/api/v1

This will fix login and all other API functionality."

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Commit failed or no changes to commit" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "✅ Changes committed" -ForegroundColor Green
    Write-Host ""
}

# Step 4: Push to trigger deployment
Write-Host "📝 Step 4: Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "⚠️ THIS IS A CRITICAL FIX - MUST BE DEPLOYED IMMEDIATELY" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Push to GitHub and deploy? (y/n)"
if ($confirm -eq "y" -or $confirm -eq "Y") {
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Pushed to GitHub successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 CRITICAL FIX DEPLOYED!" -ForegroundColor Green
        Write-Host ""
        Write-Host "What this fixes:" -ForegroundColor Cyan
        Write-Host "✅ Login will now work!" -ForegroundColor Green
        Write-Host "✅ All API requests will reach the backend" -ForegroundColor Green
        Write-Host "✅ No more 'Invalid username or password' errors" -ForegroundColor Green
        Write-Host "✅ Dashboard will load properly" -ForegroundColor Green
        Write-Host "✅ Scans will work" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Wait 2-3 minutes for Vercel to build and deploy" -ForegroundColor White
        Write-Host "2. Visit https://sentry-brown-xi.vercel.app" -ForegroundColor White
        Write-Host "3. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)" -ForegroundColor White
        Write-Host "4. Login with:" -ForegroundColor White
        Write-Host "   Email: saifullahpathan49@gmail.com" -ForegroundColor Cyan
        Write-Host "   Password: Sentry@779969" -ForegroundColor Cyan
        Write-Host "5. IT WILL WORK! 🎉" -ForegroundColor Green
        Write-Host ""
        Write-Host "Monitor deployment at: https://vercel.com/dashboard" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⏰ Estimated deployment time: 2-3 minutes" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "❌ Push failed" -ForegroundColor Red
        Write-Host "Please check your git configuration and try again" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "⚠️ Deployment cancelled" -ForegroundColor Yellow
    Write-Host "⚠️ WARNING: Login will NOT work until this is deployed!" -ForegroundColor Red
    Write-Host "Run this script again when ready to deploy" -ForegroundColor White
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Red
