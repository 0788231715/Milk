from rest_framework import viewsets, permissions
from .models import User, ManagerPermission
from .serializers import UserSerializer, ManagerPermissionSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.SUPER_ADMIN:
            return User.objects.all()
        return User.objects.filter(id=user.id)

class ManagerPermissionViewSet(viewsets.ModelViewSet):
    queryset = ManagerPermission.objects.all()
    serializer_class = ManagerPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == User.SUPER_ADMIN:
            return ManagerPermission.objects.all()
        return ManagerPermission.objects.filter(user=self.request.user)
