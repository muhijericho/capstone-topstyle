#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topstyle_business.settings')
django.setup()

from django.contrib.auth.models import User

email = 'ltv75850@gmail.com'
password = 'TempPass123!'

# Find or create user with this email
users = User.objects.filter(email__iexact=email)
if users.exists():
    user = users.first()
    print(f"Found existing user: {user.username}")
else:
    user = User.objects.create_user(
        username='ltv75850',
        email=email,
        password=password
    )
    print(f"Created new user: {user.username}")

# Activate and give admin privileges
user.is_active = True
user.is_staff = True
user.is_superuser = True
user.set_password(password)
user.save()

print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Active: {user.is_active}")
print(f"Staff: {user.is_staff}")
print(f"Superuser: {user.is_superuser}")
print(f"Password: {password}")
print("\nYou can now login with:")
print(f"  Username: {user.username}")
print(f"  Password: {password}")





