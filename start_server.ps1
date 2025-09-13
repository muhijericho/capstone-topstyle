# PowerShell script to start the Django server
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

Write-Host "Starting Django server..." -ForegroundColor Green
python manage.py runserver

Write-Host "Server stopped. Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
