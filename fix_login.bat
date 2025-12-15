@echo off
cd /d "%~dp0"
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topstyle_business.settings'); django.setup(); from django.contrib.auth.models import User; u, created = User.objects.get_or_create(username='vinceadmin', defaults={'email':'ltv75850@gmail.com','is_staff':True,'is_superuser':True}); u.is_active=True; u.is_staff=True; u.is_superuser=True; u.email='ltv75850@gmail.com'; u.set_password('Admin2024!'); u.save(); print('SUCCESS: Login with username=vinceadmin password=Admin2024!')"
pause





