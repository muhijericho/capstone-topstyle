# Clean startup script (safe copy) for TopStyle Business Management System
param(
    [switch]$SkipDependencies,
    [switch]$SkipMigrations,
    [string]$Port = "8000",
    [string]$BindHost = "0.0.0.0"
)

# Set console colors and title
$Host.UI.RawUI.WindowTitle = "TopStyle Business Management System"
$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "Green"
Clear-Host

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   TopStyle Business Management System" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

function Test-Port([int]$port) {
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $port)
        $listener.Start()
        $listener.Stop()
        return $true
    }
    catch {
        return $false
    }
}

try {
    Write-Host "[1/5] Checking system requirements..." -ForegroundColor Yellow
    if (-not (Test-Command "python")) {
        throw "Python is not installed or not in PATH. Please install Python 3.8+ and try again."
    }
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green

    if (-not (Test-Path "manage.py")) {
        throw "manage.py not found. Please run this script from the project root directory."
    }

    Write-Host "[2/5] Setting up virtual environment..." -ForegroundColor Yellow
    if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
        Write-Host "Creating virtual environment..." -ForegroundColor Cyan
        python -m venv venv
        if ($LASTEXITCODE -ne 0) { throw "Failed to create virtual environment" }
    }
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & ".\venv\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) { throw "Failed to activate virtual environment" }
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green

    if (-not $SkipDependencies) {
        Write-Host "[3/5] Installing/updating dependencies..." -ForegroundColor Yellow
        
        # Install base requirements first (without psycopg2-binary)
        Write-Host "Installing core dependencies..." -ForegroundColor Cyan
        pip install Django==5.2.7 python-decouple==3.8 whitenoise==6.11.0 Pillow==12.0.0 gunicorn==21.2.0 dj-database-url==2.1.0 django-cors-headers==4.9.0 qrcode==7.4.2 reportlab==4.4.4 openpyxl==3.1.2 crispy-bootstrap5==2025.6 twilio==9.3.1 --quiet
        
        # Try to install psycopg2-binary (optional - only needed for PostgreSQL)
        Write-Host "Installing optional PostgreSQL driver..." -ForegroundColor Cyan
        pip install psycopg2-binary==2.9.9 --quiet 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠ psycopg2-binary installation skipped (not required for SQLite)" -ForegroundColor Yellow
            Write-Host "  If you need PostgreSQL support, install Microsoft C++ Build Tools first" -ForegroundColor Gray
        } else {
            Write-Host "✓ PostgreSQL driver installed" -ForegroundColor Green
        }
        
        Write-Host "✓ Core dependencies installed successfully" -ForegroundColor Green
    } else { Write-Host "[3/5] Skipping dependency installation..." -ForegroundColor Yellow }

    if (-not $SkipMigrations) {
        Write-Host "[4/5] Running database migrations..." -ForegroundColor Yellow
        python manage.py migrate --noinput
        if ($LASTEXITCODE -ne 0) { throw "Database migration failed" }
        Write-Host "✓ Database migrations completed" -ForegroundColor Green
    } else { Write-Host "[4/5] Skipping database migrations..." -ForegroundColor Yellow }

    Write-Host "[5/5] Starting Django server..." -ForegroundColor Yellow
    if (-not (Test-Port $Port)) {
        Write-Host "⚠ Port $Port is already in use. Finding an available port..." -ForegroundColor Yellow
        $Port = 8001
        while (-not (Test-Port $Port) -and $Port -lt 8010) { $Port++ }
        if ($Port -ge 8010) { throw "No available ports found between 8000-8009" }
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "   System Ready! Starting Server..." -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Server will be available at:" -ForegroundColor White
    Write-Host "  Local:  http://localhost:$Port" -ForegroundColor Green
    Write-Host "  Network: http://$BindHost`:$Port" -ForegroundColor Green
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""

    python manage.py runserver_quiet "$BindHost`:$Port"
}
catch {
    Write-Host ""
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Make sure Python 3.8+ is installed" -ForegroundColor White
    Write-Host "2. Run this script from the project root directory" -ForegroundColor White
    Write-Host "3. Check if another server is running on port $Port" -ForegroundColor White
    Write-Host "4. Try running: python -m venv venv" -ForegroundColor White
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
finally {
    Write-Host ""
    Write-Host "Server stopped. Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
