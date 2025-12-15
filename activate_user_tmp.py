import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topstyle_business.settings')

import django
django.setup()

from django.contrib.auth.models import User

username = 'vinceadmin'
email = 'ltv75850@gmail.com'

user = User.objects.get(username=username)
user.is_active = True
user.email = email
user.save()

with open('user_activation_result.txt', 'w') as f:
    f.write(f"username={user.username}\nemail={user.email}\nis_active={user.is_active}\n")

print('Updated')

