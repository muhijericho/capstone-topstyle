@echo off
REM ========================================
REM TopStyle Business Management System
REM ONE COMMAND TO START EVERYTHING
REM ========================================
REM
REM This script will:
REM - Check Python installation
REM - Setup virtual environment if needed
REM - Install dependencies if needed
REM - Run database migrations
REM - Collect static files
REM - Start the development server
REM - Open browser automatically
REM
REM Usage: Just double-click this file or run: START_SYSTEM.bat
REM ========================================

echo.
echo ========================================
echo   TopStyle Business Management System
echo   Complete System Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/7] Python found: 
python --version

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [2/7] Virtual environment not found. Creating...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created!
) else (
    echo [2/7] Virtual environment found!
)

REM Activate virtual environment
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

REM Check if Django is installed
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo [4/7] Django not found. Installing dependencies...
    if exist "requirements.txt" (
        pip install -r requirements.txt
        if errorlevel 1 (
            echo [ERROR] Failed to install dependencies!
            pause
            exit /b 1
        )
        echo [OK] Dependencies installed!
    ) else (
        echo [WARNING] requirements.txt not found. Skipping dependency installation.
    )
) else (
    echo [4/7] Dependencies check passed!
)

REM Run migrations
echo [5/7] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo [WARNING] Migrations failed, but continuing...
)

REM Collect static files
echo [6/7] Collecting static files...
python manage.py collectstatic --noinput --clear
if errorlevel 1 (
    echo [WARNING] Static files collection failed, but continuing...
)

REM Start the system
echo.
echo ========================================
echo   Starting Development Server
echo ========================================
echo.
echo Server will be available at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
echo Opening browser in 2 seconds...
echo.

REM Open browser after delay (in background)
start /b timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000

REM Start Django server
python manage.py start_system --host 127.0.0.1 --port 8000

REM If start_system command doesn't exist, fall back to runserver
if errorlevel 1 (
    echo.
    echo [INFO] Using fallback method...
    python manage.py runserver
)

echo.
echo ========================================
echo   Server Stopped
echo ========================================
pause
