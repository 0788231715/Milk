from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrainingResourceViewSet, SystemUpdateViewSet, MilkStandardViewSet

router = DefaultRouter()
router.register(r'resources', TrainingResourceViewSet)
router.register(r'updates', SystemUpdateViewSet)
router.register(r'standards', MilkStandardViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
