# Clear Python cache files
Write-Host "Clearing Python cache..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path "." -Recurse -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Cache cleared!" -ForegroundColor Green

# Kill any existing Django processes
Write-Host "Stopping any existing Django servers..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*manage.py*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start the server
Write-Host "Starting Django server..." -ForegroundColor Yellow
python manage.py runserver























