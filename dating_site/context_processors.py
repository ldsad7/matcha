from matcha.models import Notification, UserPhoto, User
from matcha.serializers import NotificationReadSerializer


def global_user(request):
    user_id = request.user.id
    notifications = Notification.objects_.filter(user_2_id=user_id, was_read=False)
    return {
        'global_user': request.user,
        'current_user': User.objects_.get(id=user_id),
        'can_like': bool(UserPhoto.objects_.filter(user_id=user_id)),
        'notifications': NotificationReadSerializer(
            notifications, many=True
        ).data
    }
