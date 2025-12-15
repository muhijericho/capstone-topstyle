# Install dependencies with graceful handling of optional packages
# This script installs core dependencies first, then tries optional ones

Write-Host "Installing TopStyle Business System Dependencies..." -ForegroundColor Cyan
Write-Host ""

# Core dependencies (required)
Write-Host "[1/2] Installing core dependencies..." -ForegroundColor Yellow
$corePackages = @(
    "Django==5.2.7",
    "python-decouple==3.8",
    "whitenoise==6.11.0",
    "Pillow==12.0.0",
    "gunicorn==21.2.0",
    "dj-database-url==2.1.0",
    "django-cors-headers==4.9.0",
    "qrcode==7.4.2",
    "reportlab==4.4.4",
    "openpyxl==3.1.2",
    "crispy-bootstrap5==2025.6",
    "twilio==9.3.1"
)

pip install $corePackages --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Core dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: Some core dependencies may have failed to install" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/2] Installing optional PostgreSQL driver..." -ForegroundColor Yellow
pip install psycopg2-binary==2.9.9 --quiet 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PostgreSQL driver (psycopg2-binary) installed" -ForegroundColor Green
} else {
    Write-Host "⚠ psycopg2-binary skipped (optional - only needed for PostgreSQL)" -ForegroundColor Yellow
    Write-Host "  System will use SQLite by default (no action needed)" -ForegroundColor Gray
    Write-Host "  To enable PostgreSQL support later:" -ForegroundColor Gray
    Write-Host "    1. Install Microsoft C++ Build Tools" -ForegroundColor Gray
    Write-Host "    2. Re-run: pip install psycopg2-binary==2.9.9" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green






