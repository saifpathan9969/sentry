# Deploy Real Scan Integration

Write-Host "Deploying Real Scan Integration" -ForegroundColor Cyan
Write-Host ""

# Commit backend changes
Write-Host "Committing backend changes..." -ForegroundColor Yellow
Push-Location backend
git add app/scanners/ app/workers/scan_worker.py
git commit -m "Integrate real pentest brain scanning"
git push origin main
Pop-Location

Write-Host ""
Write-Host "Updating submodule reference..." -ForegroundColor Yellow
git add backend deploy-scan-fix.ps1
git commit -m "Update backend submodule - real scan integration"
git push origin main

Write-Host ""
Write-Host "Done! Scans will now be real." -ForegroundColor Green
