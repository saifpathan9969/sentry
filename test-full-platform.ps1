#!/usr/bin/env pwsh

# Test Full Platform - Frontend + Backend Integration
param(
    [Parameter(Mandatory=$true)]
    [string]$FrontendUrl
)

Write-Host "🧪 Testing Full Platform Integration..." -ForegroundColor Cyan
Write-Host "Frontend URL: $FrontendUrl" -ForegroundColor Yellow
Write-Host "Backend URL: https://sentry-backend-1.onrender.com" -ForegroundColor Yellow

try {
    # Test 1: Backend Health Check
    Write-Host "`n1️⃣ Testing Backend Health..." -ForegroundColor Blue
    $healthResponse = Invoke-RestMethod -Uri "https://sentry-backend-1.onrender.com/health" -Method GET
    Write-Host "✅ Backend Health: $($healthResponse.status)" -ForegroundColor Green
    
    # Test 2: Frontend Accessibility
    Write-Host "`n2️⃣ Testing Frontend Accessibility..." -ForegroundColor Blue
    try {
        $frontendResponse = Invoke-WebRequest -Uri $FrontendUrl -Method GET -TimeoutSec 10
        Write-Host "✅ Frontend Status: $($frontendResponse.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Frontend not accessible: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test 3: Backend Authentication
    Write-Host "`n3️⃣ Testing Backend Authentication..." -ForegroundColor Blue
    $loginData = @{
        email = "saifullahpathan49@gmail.com"
        password = "Sentry@779969"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod -Uri "https://sentry-backend-1.onrender.com/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"
    Write-Host "✅ Authentication Working!" -ForegroundColor Green
    Write-Host "   Token: $($loginResponse.access_token.Substring(0,30))..." -ForegroundColor White
    
    # Test 4: CORS Check (simulate frontend request)
    Write-Host "`n4️⃣ Testing CORS Configuration..." -ForegroundColor Blue
    $headers = @{
        'Origin' = $FrontendUrl
        'Content-Type' = 'application/json'
    }
    
    try {
        $corsResponse = Invoke-RestMethod -Uri "https://sentry-backend-1.onrender.com/api/v1/auth/login" -Method POST -Body $loginData -Headers $headers
        Write-Host "✅ CORS Working!" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  CORS might need updating" -ForegroundColor Yellow
        Write-Host "   Add $FrontendUrl to backend CORS settings" -ForegroundColor White
    }
    
    Write-Host "`n🎉 PLATFORM INTEGRATION TEST COMPLETE!" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode
        Write-Host "Status Code: $statusCode" -ForegroundColor Red
    }
}

Write-Host "`n📋 Manual Testing Steps:" -ForegroundColor Cyan
Write-Host "1. Visit: $FrontendUrl" -ForegroundColor White
Write-Host "2. Login with: saifullahpathan49@gmail.com / Sentry@779969" -ForegroundColor White
Write-Host "3. Check browser console for API calls" -ForegroundColor White
Write-Host "4. Test Neural Brain visualization" -ForegroundColor White
Write-Host "5. Create a security scan" -ForegroundColor White