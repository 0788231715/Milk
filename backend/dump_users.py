import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User

print("USER ACCOUNT LIST")
print("-" * 30)
for user in User.objects.all():
    print(f"Username: {user.username:15} | Role: {user.role:15} | Email: {user.email}")
print("-" * 30)
print("Note: Passwords are encrypted (hashed) and cannot be recovered in plain text.")
