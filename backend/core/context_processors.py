from communication.models import ChatMessage, Notification
from django.db.models import Q

def unread_counts(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': Notification.objects.filter(user=request.user, is_read=False).count(),
            'unread_messages_count': ChatMessage.objects.filter(receiver=request.user, is_read=False).count(),
        }
    return {
        'unread_notifications_count': 0,
        'unread_messages_count': 0,
    }
