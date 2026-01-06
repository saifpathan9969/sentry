#!/usr/bin/env pwsh

# Initialize Render Database via API
param(
    [Parameter(Mandatory=$true)]
    [string]$BackendUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$SecretKey
)

Write-Host "🚀 Initializing Render Database..." -ForegroundColor Cyan
Write-Host "Backend URL: $BackendUrl" -ForegroundColor Yellow

try {
    # First check database status
    Write-Host "`n📊 Checking database status..." -ForegroundColor Blue
    $statusResponse = Invoke-RestMethod -Uri "$BackendUrl/api/v1/setup/database-status" -Method GET
    
    Write-Host "Database Status:" -ForegroundColor Green
    Write-Host "- Total Users: $($statusResponse.total_users)" -ForegroundColor White
    Write-Host "- Database Ready: $($statusResponse.database_ready)" -ForegroundColor White
    
    if ($statusResponse.owner_accounts.Count -gt 0) {
        Write-Host "`n👥 Existing Owner Accounts:" -ForegroundColor Green
        foreach ($owner in $statusResponse.owner_accounts) {
            Write-Host "  - Email: $($owner.email)" -ForegroundColor White
            Write-Host "    Tier: $($owner.tier)" -ForegroundColor White
            Write-Host "    Status: $($owner.subscription_status)" -ForegroundColor White
        }
    }
    
    # Initialize database if needed
    if (-not $statusResponse.database_ready) {
        Write-Host "`n🔧 Initializing database with owner accounts..." -ForegroundColor Blue
        
        $initData = @{
            secret_key = $SecretKey
        } | ConvertTo-Json
        
        $initResponse = Invoke-RestMethod -Uri "$BackendUrl/api/v1/setup/initialize-database" -Method POST -Body $initData -ContentType "application/json"
        
        Write-Host "`n✅ Database Initialization Complete!" -ForegroundColor Green
        Write-Host "Status: $($initResponse.status)" -ForegroundColor White
        Write-Host "Message: $($initResponse.message)" -ForegroundColor White
        
        Write-Host "`n👥 Created Owner Accounts:" -ForegroundColor Green
        foreach ($owner in $initResponse.created_owners) {
            Write-Host "  - Email: $($owner.email)" -ForegroundColor White
            Write-Host "    User ID: $($owner.user_id)" -ForegroundColor White
            Write-Host "    Tier: $($owner.tier)" -ForegroundColor White
        }
        
        Write-Host "`n🔑 Login Credentials:" -ForegroundColor Yellow
        Write-Host "  Emails: $($initResponse.login_credentials.emails -join ', ')" -ForegroundColor White
        Write-Host "  Password: $($initResponse.login_credentials.password)" -ForegroundColor White
    } else {
        Write-Host "`n✅ Database already initialized!" -ForegroundColor Green
    }
    
    # Test login with first owner account
    Write-Host "`n🧪 Testing login..." -ForegroundColor Blue
    $loginData = @{
        email = "saifullahpathan49@gmail.com"
        password = "sentry@779969"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod -Uri "$BackendUrl/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"
    
    Write-Host "✅ Login Test Successful!" -ForegroundColor Green
    Write-Host "Access Token: $($loginResponse.access_token.Substring(0,50))..." -ForegroundColor White
    Write-Host "Token Type: $($loginResponse.token_type)" -ForegroundColor White
    
    Write-Host "`n🎉 RENDER BACKEND FULLY OPERATIONAL!" -ForegroundColor Green
    Write-Host "Your backend is ready for frontend deployment." -ForegroundColor White
    
} catch {
    Write-Host "`n❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode
        Write-Host "Status Code: $statusCode" -ForegroundColor Red
        
        try {
            $errorContent = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "Error Details: $($errorContent.detail)" -ForegroundColor Red
        } catch {
            Write-Host "Raw Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
        }
    }
}

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Deploy frontend to Vercel" -ForegroundColor White
Write-Host "2. Set VITE_API_BASE_URL=$BackendUrl/api/v1" -ForegroundColor White
Write-Host "3. Update CORS settings with Vercel URL" -ForegroundColor White
Write-Host "4. Test complete platform" -ForegroundColor White