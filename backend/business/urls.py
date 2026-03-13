from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiteViewSet, SupplierViewSet, BuyerViewSet, WorkerViewSet, JoinRequestViewSet

router = DefaultRouter()
router.register(r'sites', SiteViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'buyers', BuyerViewSet)
router.register(r'workers', WorkerViewSet)
router.register(r'join-requests', JoinRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
