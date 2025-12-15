# TopStyle Business Management System - Server Starter
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TopStyle Business Management System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created!" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\activate.ps1"

# Check if Django is installed
Write-Host "Checking Django installation..." -ForegroundColor Yellow
try {
    python -c "import django" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Django not found"
    }
    Write-Host "Django found!" -ForegroundColor Green
} catch {
    Write-Host "Django not found! Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "Dependencies installed!" -ForegroundColor Green
    Write-Host ""
}

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
python manage.py migrate

# Start the server
Write-Host ""
Write-Host "Starting Django development server..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
python manage.py runserver