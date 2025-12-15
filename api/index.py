"""
Vercel serverless function entry point for Django application
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topstyle_business.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

# Get WSGI application
django_app = get_wsgi_application()

# Wrap with StaticFilesHandler for serving static files in development
application = StaticFilesHandler(django_app)

# Vercel Python runtime expects 'app' variable
app = application

