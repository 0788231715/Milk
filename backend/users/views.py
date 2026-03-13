from rest_framework import viewsets, permissions
from .models import User, ManagerPermission
from .serializers import UserSerializer, ManagerPermissionSerializer

from django.db.models import Max, Q, Count, OuterRef, Subquery
from communication.models import ChatMessage

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Subquery to count unread messages for THIS specific logged in user from EACH contact
        unread_messages = ChatMessage.objects.filter(
            sender=OuterRef('pk'),
            receiver=user,
            is_read=False
        ).values('sender').annotate(count=Count('pk')).values('count')

        # Subquery for last message timestamp
        last_msg = ChatMessage.objects.filter(
            Q(sender=OuterRef('pk'), receiver=user) | 
            Q(sender=user, receiver=OuterRef('pk'))
        ).values('timestamp').order_by('-timestamp')[:1]

        qs = User.objects.exclude(id=user.id).annotate(
            unread_count=Subquery(unread_messages),
            last_msg_time=Subquery(last_msg)
        ).order_by('-last_msg_time')

        if user.role in [User.SUPER_ADMIN, User.MANAGER]:
            return qs
        # Buyers/Suppliers only see Staff
        return qs.filter(role__in=[User.SUPER_ADMIN, User.MANAGER])

class ManagerPermissionViewSet(viewsets.ModelViewSet):
    queryset = ManagerPermission.objects.all()
    serializer_class = ManagerPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == User.SUPER_ADMIN:
            return ManagerPermission.objects.all()
        return ManagerPermission.objects.filter(user=self.request.user)
