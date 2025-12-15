import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topstyle_business.settings')

import django
django.setup()

from django.contrib.auth.models import User

username = 'resetadmin'
email = 'ltv75850@gmail.com'
password = 'ResetAdmin123!'

user, created = User.objects.get_or_create(username=username, defaults={'email': email})
user.email = email
user.is_active = True
if created:
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
else:
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()

with open('reset_admin_credentials.txt', 'w') as f:
    f.write(f"username={username}\npassword={password}\nemail={email}\n")

print('resetadmin ready')

