from rest_framework import viewsets, permissions
from django.db.models import Q
from .models import ChatMessage, Notification
from .serializers import ChatMessageSerializer, NotificationSerializer

from rest_framework.decorators import action
from rest_framework.response import Response

class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatMessage.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('timestamp')

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)
        if message.receiver:
            Notification.objects.create(
                user=message.receiver,
                title=f"New Message from {message.sender.username}",
                message=f"{message.content[:50]}...",
                link="/chat/"
            )

    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        sender_id = request.data.get('sender_id')
        if sender_id:
            ChatMessage.objects.filter(sender_id=sender_id, receiver=request.user, is_read=False).update(is_read=True)
            return Response({'status': 'success'})
        return Response({'status': 'error', 'message': 'sender_id required'}, status=400)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
