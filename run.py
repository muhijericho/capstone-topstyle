#!/usr/bin/env python3
"""
Auto-activation script for Django development.
This script automatically activates the virtual environment and runs Django commands.
"""
import os
import sys
import subprocess
import platform

def get_venv_activate_script():
    """Get the correct activation script for the current platform."""
    system = platform.system().lower()
    
    if system == "windows":
        return os.path.join("venv", "Scripts", "activate.bat")
    else:
        return os.path.join("venv", "bin", "activate")

def run_django_command(command):
    """Run Django command with automatic virtual environment activation."""
    venv_script = get_venv_activate_script()
    
    if not os.path.exists(venv_script):
        print("❌ Virtual environment not found!")
        print("Please create a virtual environment first:")
        print("python -m venv venv")
        return False
    
    # Build the command to run
    if platform.system().lower() == "windows":
        full_command = f'"{venv_script}" && python manage.py {command}'
        shell = True
    else:
        full_command = f'source {venv_script} && python manage.py {command}'
        shell = True
    
    try:
        print(f"🚀 Running: python manage.py {command}")
        result = subprocess.run(full_command, shell=shell, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ Command interrupted by user")
        return False

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python run.py <django_command>")
        print("Examples:")
        print("  python run.py runserver")
        print("  python run.py makemigrations")
        print("  python run.py migrate")
        print("  python run.py shell")
        return
    
    command = " ".join(sys.argv[1:])
    run_django_command(command)

if __name__ == "__main__":
    main()
