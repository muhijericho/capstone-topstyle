# TopStyle Business - Upload to GitHub Script
# Replace the GITHUB_URL below with your actual GitHub repository URL

Write-Host "=== TopStyle Business - GitHub Upload Script ===" -ForegroundColor Green
Write-Host ""

# Get GitHub repository URL from user
$githubUrl = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/repository-name.git)"

if ($githubUrl -eq "") {
    Write-Host "Error: GitHub URL is required!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Adding GitHub remote..." -ForegroundColor Yellow
git remote add origin $githubUrl

Write-Host "Setting main branch..." -ForegroundColor Yellow
git branch -M main

Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host ""
Write-Host "✅ Successfully uploaded to GitHub!" -ForegroundColor Green
Write-Host "Your repository is now available at: $githubUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to your GitHub repository" -ForegroundColor White
Write-Host "2. Copy the repository URL" -ForegroundColor White
Write-Host "3. Use it to deploy on Railway, Render, or Heroku" -ForegroundColor White
Write-Host "4. Follow the deployment guide in DEPLOYMENT_GUIDE.md" -ForegroundColor White
