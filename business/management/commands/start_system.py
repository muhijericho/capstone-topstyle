"""
ROBUST SYSTEM STARTUP COMMAND
==============================
One command to start the entire system:
    python manage.py start_system

This command will:
- Check and setup virtual environment
- Install/update dependencies
- Run database migrations
- Collect static files
- Start the development server
- Open browser automatically
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connection
import subprocess
import sys
import os
import webbrowser
import time
import threading
from pathlib import Path


class Command(BaseCommand):
    help = 'Start the entire TopStyle Business Management System with one command'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=int,
            default=8000,
            help='Port to run the server on (default: 8000)',
        )
        parser.add_argument(
            '--host',
            type=str,
            default='127.0.0.1',
            help='Host to run the server on (default: 127.0.0.1)',
        )
        parser.add_argument(
            '--no-browser',
            action='store_true',
            help='Do not open browser automatically',
        )
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip running migrations',
        )
        parser.add_argument(
            '--skip-static',
            action='store_true',
            help='Skip collecting static files',
        )
        parser.add_argument(
            '--skip-deps',
            action='store_true',
            help='Skip dependency checking',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('  TopStyle Business Management System'))
        self.stdout.write(self.style.SUCCESS('  Complete System Startup'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        # Step 1: Check Python
        if not self.check_python():
            return

        # Step 2: Check/Create Virtual Environment
        if not options['skip_deps']:
            if not self.check_virtual_environment():
                return

        # Step 3: Check/Install Dependencies
        if not options['skip_deps']:
            if not self.check_dependencies():
                return

        # Step 4: Check Database Connection
        if not self.check_database():
            return

        # Step 5: Run Migrations
        if not options['skip_migrations']:
            if not self.run_migrations():
                return

        # Step 6: Collect Static Files
        if not options['skip_static']:
            if not self.collect_static_files():
                return

        # Step 7: Verify System
        if not self.verify_system():
            return

        # Step 8: Start Server
        self.start_server(
            host=options['host'],
            port=options['port'],
            open_browser=not options['no_browser']
        )

    def check_python(self):
        """Check if Python is available and version is correct."""
        self.stdout.write(self.style.WARNING('Step 1: Checking Python installation...'))
        try:
            version = sys.version_info
            if version.major < 3 or (version.major == 3 and version.minor < 8):
                self.stdout.write(self.style.ERROR(
                    f'ERROR: Python 3.8+ required. Found Python {version.major}.{version.minor}'
                ))
                return False
            self.stdout.write(self.style.SUCCESS(
                f'✓ Python {version.major}.{version.minor}.{version.micro} found'
            ))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERROR: {str(e)}'))
            return False

    def check_virtual_environment(self):
        """Check if virtual environment exists, create if not."""
        self.stdout.write(self.style.WARNING('\nStep 2: Checking virtual environment...'))
        
        venv_path = Path('venv')
        activate_script = None
        
        if os.name == 'nt':  # Windows
            activate_script = venv_path / 'Scripts' / 'activate.bat'
            python_exe = venv_path / 'Scripts' / 'python.exe'
        else:  # Unix/Linux/Mac
            activate_script = venv_path / 'bin' / 'activate'
            python_exe = venv_path / 'bin' / 'python'
        
        if not venv_path.exists() or not python_exe.exists():
            self.stdout.write(self.style.WARNING('Virtual environment not found. Creating...'))
            try:
                subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
                self.stdout.write(self.style.SUCCESS('✓ Virtual environment created'))
            except subprocess.CalledProcessError:
                self.stdout.write(self.style.ERROR('ERROR: Failed to create virtual environment'))
                return False
        else:
            self.stdout.write(self.style.SUCCESS('✓ Virtual environment found'))
        
        return True

    def check_dependencies(self):
        """Check and install dependencies."""
        self.stdout.write(self.style.WARNING('\nStep 3: Checking dependencies...'))
        
        requirements_file = Path('requirements.txt')
        if not requirements_file.exists():
            self.stdout.write(self.style.WARNING('requirements.txt not found. Skipping dependency check.'))
            return True
        
        # Check if Django is installed
        try:
            import django
            self.stdout.write(self.style.SUCCESS('✓ Django is installed'))
        except ImportError:
            self.stdout.write(self.style.WARNING('Django not found. Installing dependencies...'))
            try:
                python_exe = self.get_python_executable()
                subprocess.run([python_exe, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
                self.stdout.write(self.style.SUCCESS('✓ Dependencies installed'))
            except subprocess.CalledProcessError:
                self.stdout.write(self.style.ERROR('ERROR: Failed to install dependencies'))
                return False
        
        return True

    def check_database(self):
        """Check database connection."""
        self.stdout.write(self.style.WARNING('\nStep 4: Checking database connection...'))
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('✓ Database connection successful'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERROR: Database connection failed: {str(e)}'))
            self.stdout.write(self.style.WARNING(
                'Please check your database settings in settings.py'
            ))
            return False

    def run_migrations(self):
        """Run database migrations."""
        self.stdout.write(self.style.WARNING('\nStep 5: Running database migrations...'))
        try:
            call_command('migrate', verbosity=1, interactive=False)
            self.stdout.write(self.style.SUCCESS('✓ Migrations completed'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERROR: Migration failed: {str(e)}'))
            return False

    def collect_static_files(self):
        """Collect static files."""
        self.stdout.write(self.style.WARNING('\nStep 6: Collecting static files...'))
        try:
            call_command('collectstatic', verbosity=1, interactive=False, clear=True)
            self.stdout.write(self.style.SUCCESS('✓ Static files collected'))
            return True
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Warning: Static files collection failed: {str(e)}'))
            self.stdout.write(self.style.WARNING('Continuing anyway...'))
            return True  # Don't fail on static files

    def verify_system(self):
        """Verify system is ready."""
        self.stdout.write(self.style.WARNING('\nStep 7: Verifying system...'))
        
        checks = [
            ('Django', self.check_django),
            ('Database', self.check_database),
            ('Settings', self.check_settings),
        ]
        
        all_ok = True
        for name, check_func in checks:
            try:
                if not check_func():
                    all_ok = False
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'ERROR checking {name}: {str(e)}'))
                all_ok = False
        
        if all_ok:
            self.stdout.write(self.style.SUCCESS('✓ System verified and ready'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Some checks failed, but continuing...'))
        
        return True

    def check_django(self):
        """Check Django installation."""
        try:
            import django
            version = django.get_version()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Django {version}'))
            return True
        except ImportError:
            self.stdout.write(self.style.ERROR('  ✗ Django not found'))
            return False

    def check_settings(self):
        """Check Django settings."""
        try:
            if hasattr(settings, 'SECRET_KEY') and settings.SECRET_KEY:
                self.stdout.write(self.style.SUCCESS('  ✓ Settings loaded'))
                return True
            else:
                self.stdout.write(self.style.ERROR('  ✗ Settings not properly configured'))
                return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Settings error: {str(e)}'))
            return False

    def start_server(self, host='127.0.0.1', port=8000, open_browser=True):
        """Start the Django development server."""
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('  Starting Development Server'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        url = f'http://{host}:{port}'
        
        self.stdout.write(self.style.SUCCESS(f'Server URL: {url}'))
        self.stdout.write(self.style.WARNING('Press Ctrl+C to stop the server\n'))
        
        # Open browser after delay
        if open_browser:
            def open_browser_delayed():
                time.sleep(2)
                try:
                    webbrowser.open(url)
                    self.stdout.write(self.style.SUCCESS(f'✓ Browser opened at {url}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not open browser: {str(e)}'))
            
            browser_thread = threading.Thread(target=open_browser_delayed)
            browser_thread.daemon = True
            browser_thread.start()
        
        # Start the server
        try:
            call_command('runserver', f'{host}:{port}', verbosity=1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n\nServer stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nERROR: Server failed to start: {str(e)}'))

    def get_python_executable(self):
        """Get the Python executable path."""
        venv_path = Path('venv')
        if os.name == 'nt':  # Windows
            python_exe = venv_path / 'Scripts' / 'python.exe'
        else:  # Unix/Linux/Mac
            python_exe = venv_path / 'bin' / 'python'
        
        if python_exe.exists():
            return str(python_exe)
        return sys.executable

