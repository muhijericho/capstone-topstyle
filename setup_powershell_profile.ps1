# PowerShell profile setup for automatic Django virtual environment
# This script adds functions to your PowerShell profile for easy Django management

$profilePath = $PROFILE.CurrentUserAllHosts

Write-Host "Setting up PowerShell profile for Django development..." -ForegroundColor Green

# Create profile directory if it doesn't exist
$profileDir = Split-Path $profilePath -Parent
if (!(Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force
}

# Django functions to add to profile
$djangoFunctions = @"

# Django Development Functions
function Start-DjangoServer {
    param([string]$ProjectPath = ".")
    
    Push-Location $ProjectPath
    try {
        if (Test-Path "venv\Scripts\Activate.ps1") {
            Write-Host "Activating virtual environment..." -ForegroundColor Green
            & ".\venv\Scripts\Activate.ps1"
            Write-Host "Starting Django server..." -ForegroundColor Green
            python manage.py runserver
        } else {
            Write-Host "Virtual environment not found!" -ForegroundColor Red
            Write-Host "Please create one with: python -m venv venv" -ForegroundColor Yellow
        }
    } finally {
        Pop-Location
    }
}

function Invoke-DjangoCommand {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Command,
        [string]$ProjectPath = "."
    )
    
    Push-Location $ProjectPath
    try {
        if (Test-Path "venv\Scripts\Activate.ps1") {
            & ".\venv\Scripts\Activate.ps1"
            python manage.py $Command
        } else {
            Write-Host "Virtual environment not found!" -ForegroundColor Red
        }
    } finally {
        Pop-Location
    }
}

# Aliases for quick access
Set-Alias -Name djrun -Value Start-DjangoServer
Set-Alias -Name djcmd -Value Invoke-DjangoCommand

Write-Host "Django functions added to PowerShell profile!" -ForegroundColor Green
Write-Host "Usage:" -ForegroundColor Yellow
Write-Host "  djrun                    # Start Django server"
Write-Host "  djcmd makemigrations     # Run Django commands"
Write-Host "  djcmd migrate            # Run Django commands"

"@

# Add functions to profile
Add-Content -Path $profilePath -Value $djangoFunctions

Write-Host "✅ PowerShell profile updated successfully!" -ForegroundColor Green
Write-Host "Restart PowerShell or run: . `$PROFILE" -ForegroundColor Yellow
