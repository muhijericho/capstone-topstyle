#!/usr/bin/env python3
"""
TopStyle Business Management System - Auto Startup Script
This script automatically sets up and runs the entire system with one command.
"""

import os
import sys
import subprocess
import platform
import time
import webbrowser
from pathlib import Path

class TopStyleAutoStart:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.activate_script = self.get_activate_script()
        self.port = 8000
        self.host = "0.0.0.0"
        
    def get_activate_script(self):
        """Get the correct activation script for the current platform."""
        system = platform.system().lower()
        if system == "windows":
            return self.venv_path / "Scripts" / "activate.bat"
        else:
            return self.venv_path / "Scripts" / "activate"
    
    def print_header(self):
        """Print the startup header."""
        print("\n" + "="*50)
        print("   TopStyle Business Management System")
        print("   Auto Startup Script")
        print("="*50)
        print()
    
    def print_step(self, step, total, message):
        """Print a step with progress indicator."""
        print(f"[{step}/{total}] {message}...")
    
    def print_success(self, message):
        """Print success message."""
        print(f"[SUCCESS] {message}")
    
    def print_error(self, message):
        """Print error message."""
        print(f"[ERROR] {message}")
    
    def print_warning(self, message):
        """Print warning message."""
        print(f"[WARNING] {message}")
    
    def check_python(self):
        """Check if Python is available."""
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True, check=True)
            self.print_success(f"Python found: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_error("Python is not installed or not in PATH")
            return False
    
    def check_project_structure(self):
        """Check if we're in the right directory."""
        if not (self.project_root / "manage.py").exists():
            self.print_error("manage.py not found. Please run from project root.")
            return False
        return True
    
    def setup_virtual_environment(self):
        """Set up virtual environment if it doesn't exist."""
        if not self.venv_path.exists():
            self.print_step(2, 6, "Creating virtual environment")
            try:
                subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], 
                             check=True, cwd=self.project_root)
                self.print_success("Virtual environment created")
            except subprocess.CalledProcessError:
                self.print_error("Failed to create virtual environment")
                return False
        else:
            self.print_success("Virtual environment found")
        return True
    
    def install_dependencies(self):
        """Install project dependencies."""
        self.print_step(3, 6, "Installing dependencies")
        try:
            # Use the virtual environment's pip
            pip_path = self.venv_path / "Scripts" / "pip.exe" if platform.system().lower() == "windows" else self.venv_path / "bin" / "pip"
            
            subprocess.run([str(pip_path), "install", "-r", "requirements.txt", "--quiet"], 
                         check=True, cwd=self.project_root)
            self.print_success("Dependencies installed")
            return True
        except subprocess.CalledProcessError:
            self.print_warning("Some dependencies may not have installed correctly")
            return True  # Continue anyway
    
    def run_migrations(self):
        """Run database migrations."""
        self.print_step(4, 6, "Running database migrations")
        try:
            # Use the virtual environment's python
            python_path = self.venv_path / "Scripts" / "python.exe" if platform.system().lower() == "windows" else self.venv_path / "bin" / "python"
            
            subprocess.run([str(python_path), "manage.py", "migrate", "--noinput"], 
                         check=True, cwd=self.project_root)
            self.print_success("Database migrations completed")
            return True
        except subprocess.CalledProcessError:
            self.print_error("Database migration failed")
            return False
    
    def collect_static_files(self):
        """Collect static files for production."""
        self.print_step(5, 6, "Collecting static files")
        try:
            python_path = self.venv_path / "Scripts" / "python.exe" if platform.system().lower() == "windows" else self.venv_path / "bin" / "python"
            
            subprocess.run([str(python_path), "manage.py", "collectstatic", "--noinput"], 
                         check=True, cwd=self.project_root)
            self.print_success("Static files collected")
            return True
        except subprocess.CalledProcessError:
            self.print_warning("Static file collection failed (this is usually okay for development)")
            return True
    
    def start_server(self):
        """Start the Django development server."""
        self.print_step(6, 6, "Starting Django server")
        
        print("\n" + "="*50)
        print("   System Ready! Starting Server...")
        print("="*50)
        print()
        print("Server will be available at:")
        print(f"  Local:  http://localhost:{self.port}")
        print(f"  Network: http://{self.host}:{self.port}")
        print()
        print("Press Ctrl+C to stop the server")
        print()
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open(f"http://localhost:{self.port}")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        try:
            # Use the virtual environment's python
            python_path = self.venv_path / "Scripts" / "python.exe" if platform.system().lower() == "windows" else self.venv_path / "bin" / "python"
            
            subprocess.run([str(python_path), "manage.py", "runserver", f"{self.host}:{self.port}"], 
                         cwd=self.project_root)
        except KeyboardInterrupt:
            print("\n\nServer stopped by user.")
        except Exception as e:
            self.print_error(f"Server failed to start: {e}")
            return False
        
        return True
    
    def run(self):
        """Main run method."""
        self.print_header()
        
        # Step 1: Check Python
        if not self.check_python():
            return False
        
        # Step 2: Check project structure
        if not self.check_project_structure():
            return False
        
        # Step 3: Setup virtual environment
        if not self.setup_virtual_environment():
            return False
        
        # Step 4: Install dependencies
        if not self.install_dependencies():
            return False
        
        # Step 5: Run migrations
        if not self.run_migrations():
            return False
        
        # Step 6: Collect static files
        self.collect_static_files()
        
        # Step 7: Start server
        return self.start_server()

def main():
    """Main entry point."""
    try:
        auto_start = TopStyleAutoStart()
        success = auto_start.run()
        
        if not success:
            print("\n" + "="*50)
            print("   Startup Failed!")
            print("="*50)
            print("\nTroubleshooting tips:")
            print("1. Make sure Python 3.8+ is installed")
            print("2. Run this script from the project root directory")
            print("3. Check if another server is running on port 8000")
            print("4. Try running: python -m venv venv")
            print("\nPress Enter to exit...")
            input()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nStartup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)

if __name__ == "__main__":
    main()
