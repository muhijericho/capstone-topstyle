@echo off
echo ========================================
echo TopStyle Business - Vercel Setup Helper
echo ========================================
echo.

echo [1/4] Setting environment variables...
echo.
echo Opening Vercel Dashboard in your browser...
echo Please add these environment variables manually:
echo.
echo SECRET_KEY: (+ny-r#jhv9f(kdpl_r69pt2se6%6r6z0(^67ivz2%%$b(kd0q
echo DEBUG: False
echo ALLOWED_HOSTS: *.vercel.app,topstyle-business-*.vercel.app
echo.
start https://vercel.com/lagrimas-vince-ps-projects/topstyle-business/settings/environment-variables
echo.
pause

echo.
echo [2/4] Setting up database...
echo.
echo Opening Supabase (easiest free PostgreSQL option)...
start https://supabase.com/dashboard/projects
echo.
echo Follow these steps:
echo 1. Click "New Project"
echo 2. Name: topstyle-business
echo 3. Set a password (SAVE IT!)
echo 4. Choose region
echo 5. Click "Create new project"
echo 6. Wait 2 minutes
echo 7. Go to Settings -^> Database
echo 8. Copy the "Connection string -^> URI"
echo 9. Add it as DATABASE_URL in Vercel environment variables
echo.
pause

echo.
echo [3/4] Pulling environment variables and running migrations...
vercel env pull .env.local
echo.
python manage.py migrate
echo.

echo [4/4] Creating admin user (optional)...
echo.
set /p create_admin="Create admin user? (y/n): "
if /i "%create_admin%"=="y" (
    python manage.py createsuperuser
)

echo.
echo [5/5] Redeploying to Vercel...
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
















