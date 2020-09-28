from django.http import Http404
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
    first_user_id, second_user_id = list(map(int, room_name.split('_')))
    messages = sorted(Message.objects_.filter(
        user_1_id=first_user_id, user_2_id=second_user_id
    ), key=lambda elem: elem.created)
    if request.user.id == first_user_id:
        try:
            interlocutor = User.objects_.get(id=first_user_id).username
        except Exception:
            raise Http404(f"Пользователя с данным id ({first_user_id}) не существует в базе")
    context = {
        'room_name': room_name,
        'messages': messages,
        'interlocutor': interlocutor
    }
    return render(request, 'chat/room.html', context)
