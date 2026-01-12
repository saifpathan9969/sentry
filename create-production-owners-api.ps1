# Create Production Owner Accounts via API
Write-Host "Creating production owner accounts..." -ForegroundColor Cyan
Write-Host ""

$backendUrl = "https://sentry-backend-1.onrender.com/api/v1"

# Owner accounts to create
$owners = @(
    @{
        email = "saifullahpathan49@gmail.com"
        password = "Sentry@779969"
        full_name = "Saifullah Pathan"
    },
    @{
        email = "saifullah.pathan24@sanjivani.edu.in"
        password = "Sentry@779969"
        full_name = "Saifullah Pathan"
    }
)

foreach ($owner in $owners) {
    Write-Host "Creating account: $($owner.email)" -ForegroundColor Yellow
    
    try {
        $registerData = @{
            email = $owner.email
            password = $owner.password
            full_name = $owner.full_name
        } | ConvertTo-Json

        $headers = @{
            "Content-Type" = "application/json"
        }

        $response = Invoke-RestMethod -Uri "$backendUrl/auth/register" -Method Post -Body $registerData -Headers $headers -TimeoutSec 15
        Write-Host "   Account created!" -ForegroundColor Green
        Write-Host "   User ID: $($response.user.id)" -ForegroundColor Gray
        Write-Host "   Tier: $($response.user.tier)" -ForegroundColor Gray
    } catch {
        $errorMessage = $_.Exception.Message
        if ($errorMessage -like "*already registered*") {
            Write-Host "   Account already exists" -ForegroundColor Yellow
            
            # Try to login to verify
            try {
                $loginData = @{
                    email = $owner.email
                    password = $owner.password
                } | ConvertTo-Json

                $loginResponse = Invoke-RestMethod -Uri "$backendUrl/auth/login" -Method Post -Body $loginData -Headers $headers -TimeoutSec 15
                Write-Host "   Login verified!" -ForegroundColor Green
                Write-Host "   Tier: $($loginResponse.user.tier)" -ForegroundColor Gray
            } catch {
                Write-Host "   Login failed - password might be wrong" -ForegroundColor Red
            }
        } else {
            Write-Host "   Error: $errorMessage" -ForegroundColor Red
        }
    }
    Write-Host ""
}

Write-Host "Done!" -ForegroundColor Green
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Cyan
Write-Host "  Email: saifullahpathan49@gmail.com" -ForegroundColor White
Write-Host "  Email: saifullah.pathan24@sanjivani.edu.in" -ForegroundColor White
Write-Host "  Password: Sentry@779969" -ForegroundColor White
