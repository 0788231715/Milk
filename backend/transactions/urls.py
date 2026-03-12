from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MilkSupplyRecordViewSet, MilkSaleRecordViewSet, PaymentRecordViewSet, DashboardView

router = DefaultRouter()
router.register(r'supply', MilkSupplyRecordViewSet)
router.register(r'sales', MilkSaleRecordViewSet)
router.register(r'payments', PaymentRecordViewSet)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='api-dashboard'),
    path('', include(router.urls)),
]
