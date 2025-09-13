#!/usr/bin/env python3
"""
Environment setup script for Django development.
This script ensures the virtual environment is properly configured.
"""
import os
import sys
import subprocess
import platform

def check_virtual_environment():
    """Check if virtual environment is properly activated."""
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    # Check if Django is accessible
    try:
        import django
        django_version = django.get_version()
        print(f"✅ Django {django_version} is accessible")
        return True
    except ImportError:
        print("❌ Django is not accessible")
        return False

def activate_virtual_environment():
    """Activate the virtual environment."""
    venv_path = os.path.join("venv", "Scripts", "activate.bat")
    
    if not os.path.exists(venv_path):
        print("❌ Virtual environment not found!")
        print("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Virtual environment created")
        except subprocess.CalledProcessError:
            print("❌ Failed to create virtual environment")
            return False
    
    print("🔄 Activating virtual environment...")
    if platform.system().lower() == "windows":
        activate_script = os.path.join("venv", "Scripts", "activate.bat")
        subprocess.run([activate_script], shell=True)
    else:
        activate_script = os.path.join("venv", "bin", "activate")
        subprocess.run(["source", activate_script], shell=True)
    
    return True

def install_requirements():
    """Install requirements if needed."""
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        print("📦 Installing requirements...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], check=True)
            print("✅ Requirements installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            return False
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up Django development environment...")
    
    # Check if already in virtual environment
    if check_virtual_environment():
        print("✅ Environment is ready!")
        return True
    
    # Activate virtual environment
    if not activate_virtual_environment():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Final check
    if check_virtual_environment():
        print("✅ Environment setup complete!")
        return True
    else:
        print("❌ Environment setup failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
