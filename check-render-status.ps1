#!/usr/bin/env pwsh
# Script to help identify the correct Render deployment URL

Write-Host "🔍 Checking Render Deployment Status" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

Write-Host "`n📋 Service Information from render.yaml:" -ForegroundColor Cyan
Write-Host "Service Name: sentry-fullstack" -ForegroundColor White
Write-Host "Service ID: srv-d5ikh01r0fns73bb2fg0 (from your dashboard URL)" -ForegroundColor White

Write-Host "`n🌐 Possible URLs to check:" -ForegroundColor Cyan
$possibleUrls = @(
    "https://sentry-fullstack.onrender.com",
    "https://sentry-fullstack-d5ikh01r0fns73bb2fg0.onrender.com",
    "https://srv-d5ikh01r0fns73bb2fg0.onrender.com"
)

foreach ($url in $possibleUrls) {
    Write-Host "Testing: $url" -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 10 -ErrorAction Stop
        Write-Host "✅ SUCCESS: $url is accessible!" -ForegroundColor Green
        Write-Host "   Status: $($response.StatusCode)" -ForegroundColor White
        if ($response.Content -like "*SENTRY SECURITY*") {
            Write-Host "   ✅ Contains our Sentry Security app!" -ForegroundColor Green
        } elseif ($response.Content -like "*Caesar Cipher*") {
            Write-Host "   ❌ This is the CTF solver app, not our Sentry app" -ForegroundColor Red
        } else {
            Write-Host "   ❓ Unknown content" -ForegroundColor Yellow
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode) {
            Write-Host "   ❌ HTTP $statusCode" -ForegroundColor Red
        } else {
            Write-Host "   ❌ Not accessible: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Write-Host ""
}

Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Check your Render dashboard for the actual service URL" -ForegroundColor White
Write-Host "2. Look for any build/deployment errors in the logs" -ForegroundColor White
Write-Host "3. Verify the GitHub repository is connected correctly" -ForegroundColor White
Write-Host "4. Check if the service is using the correct branch (main)" -ForegroundColor White

Write-Host "`n🔧 If deployment failed, try:" -ForegroundColor Cyan
Write-Host "1. Manual redeploy from Render dashboard" -ForegroundColor White
Write-Host "2. Clear build cache and redeploy" -ForegroundColor White
Write-Host "3. Check build logs for specific errors" -ForegroundColor White

Write-Host "`n💡 The vinsmoke-2.onrender.com URL appears to be hosting a different app" -ForegroundColor Yellow
Write-Host "   This suggests either:" -ForegroundColor White
Write-Host "   - Our service has a different URL" -ForegroundColor White
Write-Host "   - The deployment has not completed successfully" -ForegroundColor White
Write-Host "   - There is a configuration mismatch" -ForegroundColor White