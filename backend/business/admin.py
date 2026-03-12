from django.contrib import admin
from .models import Site, Supplier, Buyer, Worker, Announcement, JoinRequest

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'site', 'contact', 'current_balance')
    list_filter = ('site',)
    search_fields = ('name', 'contact')

@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'current_balance')
    search_fields = ('name', 'contact')

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'base_pay')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'request_type', 'status', 'created_at')
    list_filter = ('request_type', 'status')
    search_fields = ('name', 'phone')
