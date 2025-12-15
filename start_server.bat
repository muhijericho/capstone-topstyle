@echo off
echo ========================================
echo TopStyle Business Management System
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if Django is installed
echo Checking Django installation...
python -c "import django" 2>nul
if errorlevel 1 (
    echo Django not found! Installing dependencies...
    pip install -r requirements.txt
    echo Dependencies installed!
    echo.
)

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Start the server
echo.
echo Starting Django development server...
echo ========================================
echo Server will be available at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo ========================================
echo.
python manage.py runserver

pause