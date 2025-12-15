"""
One-time script to run migrations on Vercel deployment
This can be run as a build command or manually
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topstyle_business.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    # Run migrations
    print("Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    print("Migrations completed!")
    
    # Optional: Create superuser if doesn't exist
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        print("Creating default admin user...")
        User.objects.create_superuser('admin', 'admin@topstyle.com', 'admin123')
        print("Default admin user created!")
        print("Username: admin")
        print("Password: admin123")
        print("⚠️ Please change this password immediately after first login!")
















