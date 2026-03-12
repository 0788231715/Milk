from rest_framework import serializers
from .models import MilkSupplyRecord, MilkSaleRecord, PaymentRecord, Expense, MilkLoss

class ExpenseSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.name', read_only=True)
    class Meta:
        model = Expense
        fields = ['id', 'site', 'site_name', 'category', 'amount', 'description', 'date']

class MilkLossSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.name', read_only=True)
    class Meta:
        model = MilkLoss
        fields = ['id', 'site', 'site_name', 'litres', 'reason', 'date']

class MilkSupplyRecordSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True)

    class Meta:
        model = MilkSupplyRecord
        fields = ['id', 'supplier', 'supplier_name', 'site', 'site_name', 'litres', 'price_per_litre', 'total_cost', 'quality_rating', 'date']

class MilkSaleRecordSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.name', read_only=True)
    site_source_name = serializers.CharField(source='site_source.name', read_only=True)

    class Meta:
        model = MilkSaleRecord
        fields = ['id', 'buyer', 'buyer_name', 'site_source', 'site_source_name', 'litres', 'price_per_litre', 'total_revenue', 'date']

class PaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecord
        fields = '__all__'
