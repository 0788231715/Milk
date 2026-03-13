from rest_framework import viewsets, permissions
from .models import Site, Supplier, Buyer, Worker, JoinRequest
from .serializers import SiteSerializer, SupplierSerializer, BuyerSerializer, WorkerSerializer, JoinRequestSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class JoinRequestViewSet(viewsets.ModelViewSet):
    queryset = JoinRequest.objects.all().order_by('-created_at')
    serializer_class = JoinRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        join_request = self.get_object()
        join_request.status = 'APPROVED'
        join_request.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        join_request = self.get_object()
        join_request.status = 'REJECTED'
        join_request.save()
        return Response({'status': 'rejected'})

class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

class BuyerViewSet(viewsets.ModelViewSet):
    queryset = Buyer.objects.all()
    serializer_class = BuyerSerializer
    permission_classes = [permissions.IsAuthenticated]

class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = [permissions.IsAuthenticated]
