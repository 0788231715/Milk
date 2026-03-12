from django.db import models
from django.conf import settings

class TrainingResource(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField(help_text="Main content or body of the training material")
    file = models.FileField(upload_to='training_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

class SystemUpdate(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class MilkStandard(models.Model):
    title = models.CharField(max_length=255, default="Current Milk Standard")
    min_fat_content = models.DecimalField(max_digits=5, decimal_places=2, help_text="Minimum fat percentage")
    max_temperature = models.DecimalField(max_digits=5, decimal_places=2, help_text="Maximum temperature in Celsius")
    base_price_per_litre = models.DecimalField(max_digits=10, decimal_places=2)
    guidelines = models.TextField(help_text="General quality guidelines")
    effective_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.effective_date}"
