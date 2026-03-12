from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import MilkSupplyRecord, MilkSaleRecord, PaymentRecord
from business.models import Supplier, Buyer
from .serializers import MilkSupplyRecordSerializer, MilkSaleRecordSerializer, PaymentRecordSerializer

class MilkSupplyRecordViewSet(viewsets.ModelViewSet):
    queryset = MilkSupplyRecord.objects.all()
    serializer_class = MilkSupplyRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['supplier', 'site', 'date', 'quality_rating']
    ordering_fields = ['date', 'litres']

    def perform_create(self, serializer):
        record = serializer.save()
        # Update supplier balance (Credit them)
        supplier = record.supplier
        supplier.current_balance += record.total_cost
        supplier.save()

class MilkSaleRecordViewSet(viewsets.ModelViewSet):
    queryset = MilkSaleRecord.objects.all()
    serializer_class = MilkSaleRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['buyer', 'site_source', 'date']
    ordering_fields = ['date', 'litres']

    def perform_create(self, serializer):
        record = serializer.save()
        # Update buyer balance (Debit them)
        buyer = record.buyer
        buyer.current_balance += record.total_revenue
        buyer.save()

class PaymentRecordViewSet(viewsets.ModelViewSet):
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment_type', 'supplier', 'buyer', 'worker', 'date']
    ordering_fields = ['date', 'amount']

    def perform_create(self, serializer):
        payment = serializer.save()
        # Update balances based on payment type
        if payment.payment_type == 'SUPPLIER' and payment.supplier:
            payment.supplier.current_balance -= payment.amount
            payment.supplier.save()
        elif payment.payment_type == 'BUYER' and payment.buyer:
            payment.buyer.current_balance -= payment.amount
            payment.buyer.save()
        # Worker payments don't necessarily affect a 'balance' field unless added to Worker model

class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        # Helper for aggregation
        def get_stats(queryset, date_field='date'):
            return {
                'today': queryset.filter(**{f"{date_field}__date": today}).aggregate(total=Sum('litres'))['total'] or 0,
                'week': queryset.filter(**{f"{date_field}__date__gte": week_start}).aggregate(total=Sum('litres'))['total'] or 0,
                'month': queryset.filter(**{f"{date_field}__date__gte": month_start}).aggregate(total=Sum('litres'))['total'] or 0,
            }

        def get_financials(queryset, amount_field, date_field='date'):
            return {
                'today': queryset.filter(**{f"{date_field}__date": today}).aggregate(total=Sum(amount_field))['total'] or 0,
                'week': queryset.filter(**{f"{date_field}__date__gte": week_start}).aggregate(total=Sum(amount_field))['total'] or 0,
                'month': queryset.filter(**{f"{date_field}__date__gte": month_start}).aggregate(total=Sum(amount_field))['total'] or 0,
            }

        # Milk Stats
        supply_stats = get_stats(MilkSupplyRecord.objects.all())
        sales_stats = get_stats(MilkSaleRecord.objects.all())

        # Financial Stats
        cost_stats = get_financials(MilkSupplyRecord.objects.all(), 'total_cost')
        revenue_stats = get_financials(MilkSaleRecord.objects.all(), 'total_revenue')
        
        # Calculate Profit
        profit_stats = {
            'today': revenue_stats['today'] - cost_stats['today'],
            'week': revenue_stats['week'] - cost_stats['week'],
            'month': revenue_stats['month'] - cost_stats['month'],
        }

        return Response({
            'milk_supply': supply_stats,
            'milk_sales': sales_stats,
            'costs': cost_stats,
            'revenue': revenue_stats,
            'profit': profit_stats,
        })
