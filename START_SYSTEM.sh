#!/bin/bash
# ========================================
# TopStyle Business Management System
# ONE COMMAND TO START EVERYTHING
# ========================================
#
# This script will:
# - Check Python installation
# - Setup virtual environment if needed
# - Install dependencies if needed
# - Run database migrations
# - Collect static files
# - Start the development server
# - Open browser automatically
#
# Usage: ./START_SYSTEM.sh
# ========================================

echo ""
echo "========================================"
echo "  TopStyle Business Management System"
echo "  Complete System Startup"
echo "========================================"
echo ""

# Check if Python is installed
echo "[1/7] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python is not installed!"
        echo "Please install Python 3.8+ from https://www.python.org/"
        exit 1
    else
        PYTHON_CMD=python
    fi
else
    PYTHON_CMD=python3
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "[OK] $PYTHON_VERSION"

# Check if virtual environment exists
echo "[2/7] Checking virtual environment..."
if [ ! -f "venv/bin/python" ]; then
    echo "[INFO] Virtual environment not found. Creating..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment!"
        exit 1
    fi
    echo "[OK] Virtual environment created!"
else
    echo "[OK] Virtual environment found!"
fi

# Activate virtual environment
echo "[3/7] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment!"
    exit 1
fi

# Check if Django is installed
echo "[4/7] Checking dependencies..."
if ! $PYTHON_CMD -c "import django" 2>/dev/null; then
    echo "[INFO] Django not found. Installing dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo "[ERROR] Failed to install dependencies!"
            exit 1
        fi
        echo "[OK] Dependencies installed!"
    else
        echo "[WARNING] requirements.txt not found. Skipping dependency installation."
    fi
else
    echo "[OK] Dependencies check passed!"
fi

# Run migrations
echo "[5/7] Running database migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "[WARNING] Migrations failed, but continuing..."
fi

# Collect static files
echo "[6/7] Collecting static files..."
python manage.py collectstatic --noinput --clear
if [ $? -ne 0 ]; then
    echo "[WARNING] Static files collection failed, but continuing..."
fi

# Start the system
echo ""
echo "========================================"
echo "  Starting Development Server"
echo "========================================"
echo ""
echo "Server will be available at: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo ""
echo "Opening browser in 2 seconds..."
echo ""

# Open browser after delay (background)
(sleep 2 && xdg-open http://127.0.0.1:8000 2>/dev/null || open http://127.0.0.1:8000 2>/dev/null || echo "Please open http://127.0.0.1:8000 in your browser") &

# Start Django server using the management command
if python manage.py start_system --host 127.0.0.1 --port 8000 2>/dev/null; then
    :
else
    # Fallback to runserver if start_system doesn't exist
    echo "[INFO] Using fallback method..."
    python manage.py runserver
fi

echo ""
echo "========================================"
echo "  Server Stopped"
echo "========================================"

