#!/usr/bin/env pwsh
# Test script for unified Render deployment

Write-Host "🚀 Testing Unified Render Deployment" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

$baseUrl = "https://vinsmoke-2.onrender.com"

Write-Host "🔍 Testing deployment URL: $baseUrl" -ForegroundColor Yellow

# Test 1: Health check
Write-Host "`n1. Testing health endpoint..." -ForegroundColor Cyan
try {
    $healthResponse = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET -TimeoutSec 30
    Write-Host "✅ Health check passed" -ForegroundColor Green
    Write-Host "   Status: $($healthResponse.status)" -ForegroundColor White
    Write-Host "   Environment: $($healthResponse.environment)" -ForegroundColor White
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Frontend loading
Write-Host "`n2. Testing frontend loading..." -ForegroundColor Cyan
try {
    $frontendResponse = Invoke-WebRequest -Uri $baseUrl -Method GET -TimeoutSec 30
    if ($frontendResponse.Content -like "*SENTRY SECURITY*") {
        Write-Host "✅ Frontend loaded successfully" -ForegroundColor Green
        Write-Host "   Contains login form: $($frontendResponse.Content -like '*login*')" -ForegroundColor White
        Write-Host "   Contains dashboard: $($frontendResponse.Content -like '*dashboard*')" -ForegroundColor White
    } else {
        Write-Host "❌ Frontend content not as expected" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Frontend loading failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: API endpoints
Write-Host "`n3. Testing API endpoints..." -ForegroundColor Cyan
try {
    $apiResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/" -Method GET -TimeoutSec 30
    Write-Host "✅ API root accessible" -ForegroundColor Green
} catch {
    Write-Host "❌ API root failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Login endpoint
Write-Host "`n4. Testing login endpoint..." -ForegroundColor Cyan
try {
    $loginData = @{
        email = "saifullahpathan49@gmail.com"
        password = "Sentry@779969"
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json" -TimeoutSec 30
    
    if ($loginResponse.access_token) {
        Write-Host "✅ Login successful" -ForegroundColor Green
        Write-Host "   Token received: $($loginResponse.access_token.Substring(0, 20))..." -ForegroundColor White
        
        # Test authenticated endpoint
        $headers = @{ Authorization = "Bearer $($loginResponse.access_token)" }
        $userResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/me" -Method GET -Headers $headers -TimeoutSec 30
        Write-Host "   User info: $($userResponse.email)" -ForegroundColor White
    } else {
        Write-Host "❌ Login failed - no token received" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Login test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 Deployment Test Complete!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host "If all tests passed, the deployment is working correctly!" -ForegroundColor Yellow
Write-Host "You can now access: $baseUrl" -ForegroundColor Cyan