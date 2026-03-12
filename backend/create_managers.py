import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User, ManagerPermission

def create_managers():
    for i in range(1, 6):
        username = f'manager{i}'
        email = f'manager{i}@example.com'
        password = f'manager{i}pass'
        
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, email=email, password=password, role=User.MANAGER)
            ManagerPermission.objects.create(user=user)
            print(f"Created manager: {username}")
        else:
            print(f"Manager {username} already exists")

if __name__ == "__main__":
    create_managers()
