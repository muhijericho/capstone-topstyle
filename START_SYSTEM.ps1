# ========================================
# TopStyle Business Management System
# ONE COMMAND TO START EVERYTHING
# ========================================
#
# This script will:
# - Check Python installation
# - Setup virtual environment if needed
# - Install dependencies if needed
# - Run database migrations
# - Collect static files
# - Start the development server
# - Open browser automatically
#
# Usage: Right-click and "Run with PowerShell" or run: .\START_SYSTEM.ps1
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TopStyle Business Management System" -ForegroundColor Cyan
Write-Host "  Complete System Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/7] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
Write-Host "[2/7] Checking virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[INFO] Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Virtual environment created!" -ForegroundColor Green
} else {
    Write-Host "[OK] Virtual environment found!" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "[3/7] Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to activate virtual environment!" -ForegroundColor Red
    Write-Host "You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Django is installed
Write-Host "[4/7] Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import django" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Django not found"
    }
    Write-Host "[OK] Dependencies check passed!" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Django not found. Installing dependencies..." -ForegroundColor Yellow
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Failed to install dependencies!" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        Write-Host "[OK] Dependencies installed!" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] requirements.txt not found. Skipping dependency installation." -ForegroundColor Yellow
    }
}

# Run migrations
Write-Host "[5/7] Running database migrations..." -ForegroundColor Yellow
python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Migrations failed, but continuing..." -ForegroundColor Yellow
}

# Collect static files
Write-Host "[6/7] Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --clear
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Static files collection failed, but continuing..." -ForegroundColor Yellow
}

# Start the system
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Development Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "Opening browser in 2 seconds..." -ForegroundColor Cyan
Write-Host ""

# Open browser after delay
Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:8000"

# Start Django server using the management command
try {
    python manage.py start_system --host 127.0.0.1 --port 8000
} catch {
    # Fallback to runserver if start_system doesn't exist
    Write-Host "[INFO] Using fallback method..." -ForegroundColor Yellow
    python manage.py runserver
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Server Stopped" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
