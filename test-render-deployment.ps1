#!/usr/bin/env pwsh

param(
    [Parameter(Mandatory=$true)]
    [string]$RenderUrl
)

Write-Host "🧪 Testing Render Deployment" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Testing URL: $RenderUrl" -ForegroundColor Cyan
Write-Host ""

# Test 1: Basic connectivity
Write-Host "1️⃣ Testing basic connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $RenderUrl -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Site is accessible (Status: $($response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Unexpected status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Site not accessible: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: API health check
Write-Host "2️⃣ Testing API health..." -ForegroundColor Yellow
try {
    $apiResponse = Invoke-WebRequest -Uri "$RenderUrl/health" -Method GET -TimeoutSec 10
    $healthData = $apiResponse.Content | ConvertFrom-Json
    Write-Host "   ✅ API is healthy" -ForegroundColor Green
    Write-Host "   📊 Version: $($healthData.version)" -ForegroundColor White
    Write-Host "   🌍 Environment: $($healthData.environment)" -ForegroundColor White
} catch {
    Write-Host "   ❌ API health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Frontend static files
Write-Host "3️⃣ Testing frontend assets..." -ForegroundColor Yellow
try {
    $indexResponse = Invoke-WebRequest -Uri $RenderUrl -Method GET -TimeoutSec 10
    if ($indexResponse.Content -match "<!DOCTYPE html>") {
        Write-Host "   ✅ Frontend HTML is served" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Frontend HTML not found" -ForegroundColor Red
    }
    
    if ($indexResponse.Content -match "React") {
        Write-Host "   ✅ React app detected" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  React app not detected in HTML" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Frontend test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: API endpoints
Write-Host "4️⃣ Testing API endpoints..." -ForegroundColor Yellow
$endpoints = @(
    "/api/v1/auth/me",
    "/api/v1/scans",
    "/api/v1/users/me"
)

foreach ($endpoint in $endpoints) {
    try {
        $endpointResponse = Invoke-WebRequest -Uri "$RenderUrl$endpoint" -Method GET -TimeoutSec 5
        Write-Host "   ✅ $endpoint responds (Status: $($endpointResponse.StatusCode))" -ForegroundColor Green
    } catch {
        if ($_.Exception.Response.StatusCode -eq 401) {
            Write-Host "   ✅ $endpoint requires auth (Status: 401) - Expected" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  $endpoint error: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "🎯 Manual Testing Steps:" -ForegroundColor Cyan
Write-Host "1. Open: $RenderUrl" -ForegroundColor White
Write-Host "2. Login: saifullahpathan49@gmail.com / Sentry@779969" -ForegroundColor White
Write-Host "3. Click 'New Scan'" -ForegroundColor White
Write-Host "4. Enter URL and start scan" -ForegroundColor White
Write-Host "5. Watch for green terminal output" -ForegroundColor White
Write-Host ""
Write-Host "✅ Automated tests complete!" -ForegroundColor Green