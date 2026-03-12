from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ManagerPermissionViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'permissions', ManagerPermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
