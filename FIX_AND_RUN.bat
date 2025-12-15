@echo off
echo ========================================
echo TopStyle Business Management System
echo FIXING AND STARTING SERVER
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "manage.py" (
    echo ERROR: manage.py not found!
    echo Please run this from the project root directory.
    pause
    exit /b 1
)

REM Check if virtual environment exists, if not create it
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install all requirements
echo Installing/updating all dependencies...
pip install -r requirements.txt

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Create superuser if it doesn't exist
echo Checking for superuser...
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

REM Start the server
echo.
echo ========================================
echo STARTING DJANGO SERVER
echo ========================================
echo Server URL: http://127.0.0.1:8000
echo Admin Login: admin / admin123
echo Press Ctrl+C to stop the server
echo ========================================
echo.
python manage.py runserver

pause
