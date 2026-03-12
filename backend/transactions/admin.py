from django.contrib import admin
from .models import MilkSupplyRecord, MilkSaleRecord, PaymentRecord, Loan

@admin.register(MilkSupplyRecord)
class MilkSupplyRecordAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'site', 'litres', 'total_cost', 'is_paid', 'date')
    list_editable = ('is_paid',)
    list_filter = ('site', 'is_paid', 'date')

@admin.register(MilkSaleRecord)
class MilkSaleRecordAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'site_source', 'litres', 'total_revenue', 'is_paid', 'date')
    list_editable = ('is_paid',)
    list_filter = ('site_source', 'is_paid', 'date')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('target_type', 'supplier', 'worker', 'amount', 'is_settled', 'date_given')
    list_editable = ('is_settled',)
    list_filter = ('target_type', 'is_settled')

@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('payment_type', 'amount', 'date')
    list_filter = ('payment_type', 'date')
