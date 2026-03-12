from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    SUPER_ADMIN = 'SUPER_ADMIN'
    MANAGER = 'MANAGER'
    WORKER = 'WORKER'
    SUPPLIER = 'SUPPLIER'
    BUYER = 'BUYER'

    ROLE_CHOICES = [
        (SUPER_ADMIN, 'Super Admin'),
        (MANAGER, 'Manager'),
        (WORKER, 'Worker'),
        (SUPPLIER, 'Supplier'),
        (BUYER, 'Buyer'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=WORKER)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class ManagerPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_permissions')
    assigned_site = models.ForeignKey('business.Site', on_delete=models.SET_NULL, null=True, blank=True, help_text="The site this manager is responsible for")
    can_see_revenue = models.BooleanField(default=False)
    can_see_transactions = models.BooleanField(default=False)
    can_add_users = models.BooleanField(default=False)
    can_manage_sites = models.BooleanField(default=False)
    can_edit_past_dates = models.BooleanField(default=False)

    def __str__(self):
        return f"Permissions for {self.user.username} ({self.assigned_site.name if self.assigned_site else 'Global'})"
