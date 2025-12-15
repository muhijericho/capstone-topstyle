@echo off
echo ========================================
echo Completing Vercel Setup
echo ========================================
echo.

echo [1/3] Pulling environment variables...
vercel env pull .env.local
echo.

echo [2/3] Running database migrations...
python manage.py migrate --noinput
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Migrations failed. Please check DATABASE_URL is set correctly.
    pause
    exit /b 1
)
echo Migrations completed successfully!
echo.

echo [3/3] Creating admin user...
echo.
set /p create_admin="Create admin user? (y/n): "
if /i "%create_admin%"=="y" (
    python manage.py createsuperuser
) else (
    echo Skipping admin user creation.
)
echo.

echo [4/4] Redeploying to Vercel...
vercel --prod
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Your app should be live at:
echo https://topstyle-business-mw227psxo-lagrimas-vince-ps-projects.vercel.app
echo.
pause
















