# Test Docker deployment login
# Verify authentication works with updated credentials

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTING DOCKER DEPLOYMENT LOGIN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test credentials
$email1 = "saifullahpathan49@gmail.com"
$email2 = "saifullah.pathan24@sanjivani.edu.in"
$password = "sentry@779969"
$baseUrl = "http://localhost:8000"

Write-Host "Testing login with updated credentials..." -ForegroundColor Yellow
Write-Host ""

# Test first email
Write-Host "📧 Testing: $email1" -ForegroundColor Cyan
try {
    $loginData = @{
        email = $email1
        password = $password
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json" -TimeoutSec 10
    
    if ($response.access_token) {
        Write-Host "✅ Login successful!" -ForegroundColor Green
        Write-Host "   Access Token: $($response.access_token.Substring(0, 50))..." -ForegroundColor Gray
        
        # Test protected endpoint
        $headers = @{ Authorization = "Bearer $($response.access_token)" }
        $userResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/users/me" -Method GET -Headers $headers
        
        Write-Host "   User: $($userResponse.email)" -ForegroundColor White
        Write-Host "   Tier: $($userResponse.tier)" -ForegroundColor White
        Write-Host "   Full Name: $($userResponse.full_name)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Login failed for $email1" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test second email
Write-Host "📧 Testing: $email2" -ForegroundColor Cyan
try {
    $loginData = @{
        email = $email2
        password = $password
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json" -TimeoutSec 10
    
    if ($response.access_token) {
        Write-Host "✅ Login successful!" -ForegroundColor Green
        Write-Host "   Access Token: $($response.access_token.Substring(0, 50))..." -ForegroundColor Gray
        
        # Test protected endpoint
        $headers = @{ Authorization = "Bearer $($response.access_token)" }
        $userResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/users/me" -Method GET -Headers $headers
        
        Write-Host "   User: $($userResponse.email)" -ForegroundColor White
        Write-Host "   Tier: $($userResponse.tier)" -ForegroundColor White
        Write-Host "   Full Name: $($userResponse.full_name)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Login failed for $email2" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Test completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Your credentials:" -ForegroundColor Cyan
Write-Host "  Email: $email1" -ForegroundColor White
Write-Host "  Email: $email2" -ForegroundColor White
Write-Host "  Password: $password" -ForegroundColor White
Write-Host "  Tier: Enterprise (Full Access)" -ForegroundColor White
Write-Host ""
Write-Host "Visit: http://localhost to login and test the neural brain!" -ForegroundColor Yellow