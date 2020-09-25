from matcha.models import Notification
from matcha.serializers import NotificationReadSerializer


def global_user(request):
    return {
        'global_user': request.user,
        'notifications': NotificationReadSerializer(
            Notification.objects_.filter(user_2_id=request.user.id, was_read=False), many=True
        ).data
    }
