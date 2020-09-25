from django.shortcuts import render

from matcha.models import UsersConnect, User, Message
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
    first_user_id, second_user_id = room_name.split('_')
    if str(request.user.id) == first_user_id:
        type_ = Message.TO_1_2
    else:
        type_ = Message.TO_2_1
    messages = sorted(Message.objects_.filter(
        user_1_id=first_user_id, user_2_id=second_user_id, type=type_
    ), key=lambda elem: elem['created'])[::-1]
    context = {
        'room_name': room_name,
        'messages': messages
    }
    return render(request, 'chat/room.html', context)
