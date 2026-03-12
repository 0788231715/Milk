from django.db import models
from business.models import Site, Supplier, Buyer, Worker

from django.utils import timezone

class MilkSupplyRecord(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplies')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='supplies')
    litres = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_litre = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    quality_rating = models.IntegerField(default=5)  # 1-10
    date = models.DateTimeField(default=timezone.now)
    is_paid = models.BooleanField(default=False, help_text="Tick if the supplier has been paid for this supply")

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
    is_paid = models.BooleanField(default=False, help_text="Tick if the buyer has paid for this purchase")

    def save(self, *args, **kwargs):
        self.total_revenue = self.litres * self.price_per_litre
        super().save(*args, **kwargs)

class Loan(models.Model):
    LOAN_TARGETS = [('SUPPLIER', 'Supplier'), ('WORKER', 'Worker')]
    target_type = models.CharField(max_length=10, choices=LOAN_TARGETS)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date_given = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    is_settled = models.BooleanField(default=False, help_text="Tick when this loan is deducted from their pay")

    def __str__(self):
        return f"Loan: {self.amount} to {self.supplier if self.supplier else self.worker}"

class PaymentRecord(models.Model):
    PAYMENT_TYPES = [
        ('SUPPLIER', 'To Supplier'),
        ('BUYER', 'From Buyer'),
        ('WORKER', 'To Worker'),
    ]
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Generic relations or specific ones
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True)
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.payment_type} - {self.amount}"
