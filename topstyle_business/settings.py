"""
Django settings for topstyle_business project.
"""

import os
from pathlib import Path


# Temporarily use os.environ instead of decouple for development
def config(key, default=None, cast=None):
    value = os.environ.get(key, default)
    if cast and value is not None:
        if cast == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        elif cast == int:
            return int(value)
        elif cast == float:
            return float(value)
        elif cast == list:
            return value.split(',')
    return value

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-here-change-this-in-production-please-change-this-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Security settings
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=not DEBUG, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000 if not DEBUG else 0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF token from cookie
CSRF_USE_SESSIONS = False  # Use cookies for CSRF token (default)
CSRF_COOKIE_SAMESITE = 'Lax'  # Allow CSRF cookie to be sent with same-site requests
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,*.herokuapp.com,*.railway.app,*.vercel.app,*.render.com').split(',')



# Twilio SMS Configuration
TWILIO_ACCOUNT_SID = "SKe0f7454db3502b5dfcb32352198be4c6" # config('TWILIO_ACCOUNT_SID', default='ACc80054a9c3f513815e247eb87d46c0ac')
TWILIO_AUTH_TOKEN = "p6Qq2vjSoWNKzMLujXuhz8FJlEWLkFlg" # config('TWILIO_AUTH_TOKEN', default='8563ffc97cd3025ea911f41c60439e33')
TWILIO_PHONE_NUMBER = "+15807412415" # config('TWILIO_PHONE_NUMBER', default='+15807412415')
TWILIO_MESSAGING_SERVICE_SID = "" # config('TWILIO_MESSAGING_SERVICE_SID', default='')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'business',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'business.middleware.persistence_middleware.PersistenceMiddleware',  # Auto-save persistence middleware
]

ROOT_URLCONF = 'topstyle_business.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'business.context_processors.dark_mode_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'topstyle_business.wsgi.application'

# Database
import dj_database_url

DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL', default=f'sqlite:///{BASE_DIR}/db.sqlite3')
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# SMS Configuration (for future use)
SMS_API_KEY = config('SMS_API_KEY', default='')
SMS_SENDER_ID = config('SMS_SENDER_ID', default='TopStyle')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Email Configuration - Gmail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ltv75850@gmail.com'
EMAIL_HOST_PASSWORD = 'nvklcshcxificgby'  # Consider moving to environment variable
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_USE_SSL = False

# Password Reset Code Settings
PASSWORD_RESET_CODE_EXPIRY_MINUTES = 10  # Codes expire in 10 minutes

# Suppress development server warnings
import warnings

warnings.filterwarnings('ignore', message='.*development server.*', category=UserWarning)

# Logging Configuration
# On Vercel, filesystem is read-only, so only use console logging
IS_VERCEL = os.environ.get('VERCEL', '').lower() == '1'

# Note: Development server warnings are suppressed via the custom runserver_quiet command
# Use: python manage.py runserver_quiet instead of python manage.py runserver

# Custom filter to suppress Chrome DevTools warnings
class SuppressChromeDevToolsFilter:
    def filter(self, record):
        message = str(record.getMessage())
        return '.well-known/appspecific/com.chrome.devtools.json' not in message

class SuppressBrokenPipeFilter:
    def filter(self, record):
        """Suppress harmless 'Broken pipe' errors from Django development server"""
        message = str(record.getMessage())
        # Suppress broken pipe errors which are harmless in development
        if 'Broken pipe' in message or 'broken pipe' in message.lower():
            return False
        return True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'suppress_chrome_devtools': {
            '()': 'topstyle_business.settings.SuppressChromeDevToolsFilter',
        },
        'suppress_broken_pipe': {
            '()': 'topstyle_business.settings.SuppressBrokenPipeFilter',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['suppress_chrome_devtools', 'suppress_broken_pipe'],
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
            'filters': ['suppress_chrome_devtools', 'suppress_broken_pipe'],
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
            'filters': ['suppress_chrome_devtools', 'suppress_broken_pipe'],
        },
        'business': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Only add file handler if not on Vercel
if not IS_VERCEL:
    LOGGING['handlers']['file'] = {
        'class': 'logging.FileHandler',
        'filename': BASE_DIR / 'logs' / 'django.log',
        'formatter': 'verbose',
    }
    LOGGING['loggers']['django']['handlers'].append('file')
    LOGGING['loggers']['business']['handlers'].append('file')
    
    # Create logs directory if it doesn't exist
    logs_dir = BASE_DIR / 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

        os.makedirs(logs_dir)

        os.makedirs(logs_dir)

        os.makedirs(logs_dir)


