from django.db import models
from django.conf import settings

class Site(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supplier_profile')
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=50)
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, related_name='suppliers')
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class Buyer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_profile', null=True, blank=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=50)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class Worker(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='worker_profile')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    base_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Link to an image for advertising")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class JoinRequest(models.Model):
    TYPES = [('SUPPLIER', 'Supplier'), ('BUYER', 'Buyer')]
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    password = models.CharField(max_length=128, help_text="User's chosen password", null=True, blank=True)
    request_type = models.CharField(max_length=10, choices=TYPES)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='PENDING', choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.request_type} Request from {self.name}"
