# Fix and Run Script for TopStyle Business Management System
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Fixing Django Installation" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = "c:\Users\vince\Videos\CAPSTONE_FINAL_SYSTEM\CAPSTONE2.0_CURSUR - Copy"
Set-Location $projectPath

# Step 1: Activate virtual environment
Write-Host "[1/5] Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "✗ Virtual environment not found at .venv" -ForegroundColor Red
    Write-Host "Creating new virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    & ".venv\Scripts\Activate.ps1"
}

# Step 2: Verify Python path
Write-Host "`n[2/5] Verifying Python installation..." -ForegroundColor Yellow
$pythonExe = ".venv\Scripts\python.exe"
if (Test-Path $pythonExe) {
    $pythonVersion = & $pythonExe --version
    Write-Host "✓ Using: $pythonVersion" -ForegroundColor Green
    Write-Host "  Path: $((Resolve-Path $pythonExe).Path)" -ForegroundColor Gray
} else {
    Write-Host "✗ Python executable not found!" -ForegroundColor Red
    exit 1
}

# Step 3: Upgrade pip
Write-Host "`n[3/5] Upgrading pip..." -ForegroundColor Yellow
& $pythonExe -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green

# Step 4: Install Django and dependencies
Write-Host "`n[4/5] Installing Django and dependencies..." -ForegroundColor Yellow
& $pythonExe -m pip install Django==5.2.7 --quiet
Write-Host "✓ Django installed" -ForegroundColor Green

& $pythonExe -m pip install -r requirements.txt --quiet
Write-Host "✓ All dependencies installed" -ForegroundColor Green

# Step 5: Verify Django installation
Write-Host "`n[5/5] Verifying Django installation..." -ForegroundColor Yellow
try {
    $djangoVersion = & $pythonExe -c "import django; print(django.__version__)"
    Write-Host "✓ Django $djangoVersion is installed and working!" -ForegroundColor Green
} catch {
    Write-Host "✗ Django verification failed: $_" -ForegroundColor Red
    exit 1
}

# Run migrations
Write-Host "`nRunning database migrations..." -ForegroundColor Yellow
& $pythonExe manage.py migrate --noinput
Write-Host "✓ Migrations completed" -ForegroundColor Green

# Start server
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Starting Django Server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor White
Write-Host "  http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

& $pythonExe manage.py runserver 8000
