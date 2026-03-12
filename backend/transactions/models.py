from django.db import models
from business.models import Site, Supplier, Buyer, Worker
from django.utils import timezone

class MilkSupplyRecord(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplies')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='supplies')
    litres = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_litre = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    quality_rating = models.IntegerField(default=5)
    date = models.DateTimeField(default=timezone.now)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.total_cost = self.litres * self.price_per_litre
        super().save(*args, **kwargs)

class MilkSaleRecord(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='sales')
    site_source = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='sales')
    litres = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_litre = models.DecimalField(max_digits=10, decimal_places=2)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    date = models.DateTimeField(default=timezone.now)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.total_revenue = self.litres * self.price_per_litre
        super().save(*args, **kwargs)

class Expense(models.Model):
    CATEGORIES = [('FUEL', 'Fuel'), ('WAGES', 'Wages'), ('MAINTENANCE', 'Maintenance'), ('OTHER', 'Other')]
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=20, choices=CATEGORIES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    date = models.DateField(default=timezone.now)

class MilkLoss(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='losses')
    litres = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now)

class Loan(models.Model):
    target_type = models.CharField(max_length=10, choices=[('SUPPLIER', 'Supplier'), ('WORKER', 'Worker')])
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date_given = models.DateField(auto_now_add=True)
    is_settled = models.BooleanField(default=False)

class PaymentRecord(models.Model):
    payment_type = models.CharField(max_length=20, choices=[('SUPPLIER', 'To Supplier'), ('BUYER', 'From Buyer'), ('WORKER', 'To Worker')])
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True)
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True)
