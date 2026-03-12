from rest_framework import viewsets, permissions
from .models import TrainingResource, SystemUpdate, MilkStandard
from .serializers import TrainingResourceSerializer, SystemUpdateSerializer, MilkStandardSerializer

class TrainingResourceViewSet(viewsets.ModelViewSet):
    queryset = TrainingResource.objects.all().order_by('-created_at')
    serializer_class = TrainingResourceSerializer
    permission_classes = [permissions.IsAuthenticated]

class SystemUpdateViewSet(viewsets.ModelViewSet):
    queryset = SystemUpdate.objects.filter(is_active=True).order_by('-date')
    serializer_class = SystemUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

class MilkStandardViewSet(viewsets.ModelViewSet):
    queryset = MilkStandard.objects.all().order_by('-effective_date')
    serializer_class = MilkStandardSerializer
    permission_classes = [permissions.IsAuthenticated]
