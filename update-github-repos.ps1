# Update GitHub Repositories with Latest Neural Brain Code
# This script pushes frontend to sentry-frontend and backend to sentry-backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  UPDATING GITHUB REPOSITORIES" -ForegroundColor Cyan
Write-Host "  Latest Neural Brain Code" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is available
try {
    git --version | Out-Null
    Write-Host "Git: Available" -ForegroundColor Green
} catch {
    Write-Host "Git: Not found. Please install Git" -ForegroundColor Red
    exit 1
}

# Function to update repository
function Update-Repository {
    param(
        [string]$RepoName,
        [string]$LocalPath,
        [string]$RepoUrl
    )
    
    Write-Host ""
    Write-Host "📦 Updating $RepoName..." -ForegroundColor Yellow
    
    # Create temporary directory for the repo
    $TempDir = "temp_$RepoName"
    
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir
    }
    
    try {
        # Clone the repository
        Write-Host "   Cloning repository..." -ForegroundColor Gray
        git clone $RepoUrl $TempDir
        
        if (!(Test-Path $TempDir)) {
            Write-Host "   ❌ Failed to clone repository" -ForegroundColor Red
            return $false
        }
        
        # Remove all files except .git
        Write-Host "   Clearing old files..." -ForegroundColor Gray
        Get-ChildItem -Path $TempDir -Exclude ".git" | Remove-Item -Recurse -Force
        
        # Copy new files
        Write-Host "   Copying new files..." -ForegroundColor Gray
        Copy-Item -Path "$LocalPath\*" -Destination $TempDir -Recurse -Force
        
        # Change to repo directory
        Push-Location $TempDir
        
        # Add all files
        Write-Host "   Adding files to git..." -ForegroundColor Gray
        git add .
        
        # Check if there are changes
        $status = git status --porcelain
        if ($status) {
            # Commit changes
            Write-Host "   Committing changes..." -ForegroundColor Gray
            git commit -m "Update with latest Neural Brain features - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
            
            # Push changes
            Write-Host "   Pushing to GitHub..." -ForegroundColor Gray
            git push origin main
            
            Write-Host "   ✅ $RepoName updated successfully!" -ForegroundColor Green
        } else {
            Write-Host "   ℹ️ No changes detected in $RepoName" -ForegroundColor Blue
        }
        
        # Return to original directory
        Pop-Location
        
        # Clean up
        Remove-Item -Recurse -Force $TempDir
        
        return $true
        
    } catch {
        Write-Host "   ❌ Error updating $RepoName`: $($_.Exception.Message)" -ForegroundColor Red
        
        # Return to original directory if we're in the temp dir
        if ((Get-Location).Path.EndsWith($TempDir)) {
            Pop-Location
        }
        
        # Clean up
        if (Test-Path $TempDir) {
            Remove-Item -Recurse -Force $TempDir
        }
        
        return $false
    }
}

# Get GitHub username
$GitHubUsername = Read-Host "Enter your GitHub username"

if (-not $GitHubUsername) {
    Write-Host "❌ GitHub username is required" -ForegroundColor Red
    exit 1
}

# Repository URLs
$FrontendRepo = "https://github.com/$GitHubUsername/sentry-frontend.git"
$BackendRepo = "https://github.com/$GitHubUsername/sentry-backend.git"

Write-Host "📋 Repository Information:" -ForegroundColor Cyan
Write-Host "   Frontend: $FrontendRepo" -ForegroundColor White
Write-Host "   Backend:  $BackendRepo" -ForegroundColor White
Write-Host ""

# Confirm before proceeding
$Confirm = Read-Host "Do you want to update both repositories? (y/N)"
if ($Confirm -ne "y" -and $Confirm -ne "Y") {
    Write-Host "❌ Operation cancelled" -ForegroundColor Yellow
    exit 0
}

# Update Frontend Repository
$FrontendSuccess = Update-Repository -RepoName "sentry-frontend" -LocalPath "frontend" -RepoUrl $FrontendRepo

# Update Backend Repository  
$BackendSuccess = Update-Repository -RepoName "sentry-backend" -LocalPath "backend" -RepoUrl $BackendRepo

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  UPDATE SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($FrontendSuccess) {
    Write-Host "✅ Frontend (sentry-frontend): Updated" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend (sentry-frontend): Failed" -ForegroundColor Red
}

if ($BackendSuccess) {
    Write-Host "✅ Backend (sentry-backend): Updated" -ForegroundColor Green
} else {
    Write-Host "❌ Backend (sentry-backend): Failed" -ForegroundColor Red
}

Write-Host ""

if ($FrontendSuccess -and $BackendSuccess) {
    Write-Host "🎉 SUCCESS! Both repositories updated with latest Neural Brain code!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Deploy frontend from sentry-frontend repo to Vercel" -ForegroundColor White
    Write-Host "   2. Deploy backend from sentry-backend repo to Railway" -ForegroundColor White
    Write-Host "   3. Follow DEPLOYMENT_INSTRUCTIONS.md for complete setup" -ForegroundColor White
    Write-Host ""
    Write-Host "🔗 Your repositories are now ready for deployment!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Some repositories failed to update. Please check the errors above." -ForegroundColor Yellow
    Write-Host "You may need to manually push the changes or check repository permissions." -ForegroundColor Yellow
}

Write-Host ""