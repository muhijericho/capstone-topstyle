#!/usr/bin/env python3
"""
TopStyle Business Management System - Enhanced Run Script
This script automatically activates the virtual environment and runs Django commands.
Now includes full system startup capabilities.
"""
import os
import sys
import subprocess
import platform
import time
import webbrowser
from pathlib import Path

def get_venv_activate_script():
    """Get the correct activation script for the current platform."""
    system = platform.system().lower()
    
    if system == "windows":
        return os.path.join("venv", "Scripts", "activate.bat")
    else:
        return os.path.join("venv", "bin", "activate")

def get_python_executable():
    """Get the Python executable from virtual environment."""
    system = platform.system().lower()
    
    if system == "windows":
        return os.path.join("venv", "Scripts", "python.exe")
    else:
        return os.path.join("venv", "bin", "python")

def check_system_requirements():
    """Check if system requirements are met."""
    print("Checking system requirements...")
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"Python found: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: Python is not installed or not in PATH")
        return False
    
    # Check if we're in the right directory
    if not os.path.exists("manage.py"):
        print("ERROR: manage.py not found. Please run from project root.")
        return False
    
    print("Project structure looks good")
    return True

def setup_virtual_environment():
    """Set up virtual environment if needed."""
    venv_script = get_venv_activate_script()
    
    if not os.path.exists(venv_script):
        print("🔧 Virtual environment not found! Creating one...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("Virtual environment created")
        except subprocess.CalledProcessError:
            print("ERROR: Failed to create virtual environment")
            return False
    else:
        print("Virtual environment found")
    
    return True

def install_dependencies():
    """Install project dependencies."""
    print("Installing dependencies...")
    try:
        python_exe = get_python_executable()
        if not os.path.exists(python_exe):
            print("ERROR: Python executable not found in virtual environment")
            return False
        
        # Install core dependencies first
        core_packages = [
            "Django==5.2.7", "python-decouple==3.8", "whitenoise==6.11.0",
            "Pillow==12.0.0", "gunicorn==21.2.0", "dj-database-url==2.1.0",
            "django-cors-headers==4.9.0", "qrcode==7.4.2", "reportlab==4.4.4",
            "openpyxl==3.1.2", "crispy-bootstrap5==2025.6", "twilio==9.3.1"
        ]
        
        print("Installing core dependencies...")
        result = subprocess.run([python_exe, "-m", "pip", "install"] + core_packages + ["--quiet"],
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print("WARNING: Some core dependencies may not have installed correctly")
            print("Error:", result.stderr[:200] if result.stderr else "Unknown error")
        
        # Try to install psycopg2-binary (optional - only needed for PostgreSQL)
        print("Installing optional PostgreSQL driver...")
        result = subprocess.run([python_exe, "-m", "pip", "install", "psycopg2-binary==2.9.9", "--quiet"],
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠ psycopg2-binary installation skipped (not required for SQLite)")
            print("  If you need PostgreSQL support, install Microsoft C++ Build Tools first")
        else:
            print("✓ PostgreSQL driver installed")
        
        print("✓ Core dependencies installed successfully")
        return True
    except Exception as e:
        print(f"WARNING: Error during dependency installation: {e}")
        return True  # Continue anyway

def run_migrations():
    """Run database migrations."""
    print("Running database migrations...")
    try:
        python_exe = get_python_executable()
        subprocess.run([python_exe, "manage.py", "migrate", "--noinput"], check=True)
        print("Database migrations completed")
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Database migration failed")
        return False

def run_django_command(command):
    """Run Django command with automatic virtual environment activation."""
    venv_script = get_venv_activate_script()
    python_exe = get_python_executable()
    
    if not os.path.exists(venv_script):
        print("ERROR: Virtual environment not found!")
        print("Please create a virtual environment first:")
        print("python -m venv venv")
        return False
    
    if not os.path.exists(python_exe):
        print("ERROR: Python executable not found in virtual environment")
        return False
    
    try:
        print(f"Running: python manage.py {command}")
        
        if command == "runserver":
            # Special handling for runserver with auto-browser opening
            print("\n" + "="*50)
            print("   TopStyle Business Management System")
            print("   Development Server Starting...")
            print("="*50)
            print()
            print("Server will be available at:")
            print("  Local:  http://localhost:8000")
            print("  Network: http://0.0.0.0:8000")
            print()
            print("Press Ctrl+C to stop the server")
            print()
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(2)
                webbrowser.open("http://localhost:8000")
            
            import threading
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
        
        result = subprocess.run([python_exe, "manage.py"] + command.split(), check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Error running command: {e}")
        return False
    except KeyboardInterrupt:
        print("\nCommand interrupted by user")
        return False

def full_startup():
    """Perform full system startup."""
    print("\n" + "="*50)
    print("   TopStyle Business Management System")
    print("   Full System Startup")
    print("="*50)
    print()
    
    # Check system requirements
    if not check_system_requirements():
        return False
    
    # Setup virtual environment
    if not setup_virtual_environment():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Run migrations
    if not run_migrations():
        return False
    
    # Start server
    print("\nStarting development server...")
    return run_django_command("runserver")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("TopStyle Business Management System - Run Script")
        print("="*50)
        print()
        print("Usage: python run.py <command>")
        print()
        print("Commands:")
        print("  start, run, server    - Full system startup (recommended)")
        print("  runserver            - Start Django server only")
        print("  migrate              - Run database migrations")
        print("  makemigrations       - Create new migrations")
        print("  shell                - Open Django shell")
        print("  collectstatic        - Collect static files")
        print("  help                 - Show this help message")
        print()
        print("Examples:")
        print("  python run.py start")
        print("  python run.py runserver")
        print("  python run.py migrate")
        print()
        return
    
    command = sys.argv[1].lower()
    
    if command in ["start", "run", "server"]:
        success = full_startup()
        if not success:
            print("\nERROR: Startup failed! Check the errors above.")
            sys.exit(1)
    elif command == "help":
        main()  # Show help
    else:
        # Run specific Django command
        django_command = " ".join(sys.argv[1:])
        success = run_django_command(django_command)
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        sys.exit(1)
