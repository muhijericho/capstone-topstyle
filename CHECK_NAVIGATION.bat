@echo off
echo ========================================
echo TopStyle Navigation Validator
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_env.py first to create the virtual environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if Django is installed
python -c "import django" 2>nul
if errorlevel 1 (
    echo ERROR: Django not found in virtual environment!
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Run navigation validation
echo.
echo Running navigation validation...
echo ========================================
python check_navigation.py

REM Check result
if errorlevel 1 (
    echo.
    echo ========================================
    echo Navigation validation FAILED!
    echo Please fix the errors above.
    echo ========================================
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo Navigation validation PASSED!
    echo Your system is ready to use.
    echo ========================================
)

pause
