from django.shortcuts import render

from matcha.models import UsersConnect, User
from matcha.serializers import UserReadSerializer


def index(request):
    liked_user_ids = {
        user_connect.user_2_id for user_connect in UsersConnect.objects_.filter(user_1_id=request.user.id)
    }
    liking_user_ids = {
        user_connect.user_1_id for user_connect in UsersConnect.objects_.filter(user_2_id=request.user.id)
    }
    context = {
        'users': UserReadSerializer(User.objects_.filter(id__in=liked_user_ids & liking_user_ids), many=True).data
    }
    return render(request, 'chat/index.html', context)


def room(request, room_name):
    context = {
        'room_name': room_name,
    }
    return render(request, 'chat/room.html', context)
