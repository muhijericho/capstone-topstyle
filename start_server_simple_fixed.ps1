# Simple Django Server Starter (Fixed)
# This script starts the Django server without PowerShell output redirection errors

Write-Host "Starting Django Development Server..." -ForegroundColor Cyan
Write-Host ""

# Determine which Python to use
if (Test-Path "venv\Scripts\python.exe") {
    $pythonExe = "venv\Scripts\python.exe"
    Write-Host "Using virtual environment Python" -ForegroundColor Green
} else {
    $pythonExe = "python"
    Write-Host "Using system Python" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server - simple command without complex redirection
& $pythonExe manage.py runserver


