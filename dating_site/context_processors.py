from matcha.models import Notification, UserPhoto
from matcha.serializers import NotificationReadSerializer


def global_user(request):
    notifications = Notification.objects_.filter(user_2_id=request.user.id, was_read=False)
    return {
        'global_user': request.user,
        'can_like': bool(UserPhoto.objects_.filter(user_id=request.user.id)),
        'notifications': NotificationReadSerializer(
            notifications, many=True
        ).data
    }
