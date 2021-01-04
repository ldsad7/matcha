from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from matcha.models import UsersConnect, User, Message
from matcha.serializers import UserReadSerializer, UserSerializer


@login_required
def index(request):
    liked_user_ids = {
        user_connect.user_2_id
        for user_connect in UsersConnect.objects_.filter(user_1_id=request.user.id, type=UsersConnect.PLUS)
    }
    liking_user_ids = {
        user_connect.user_1_id
        for user_connect in UsersConnect.objects_.filter(user_2_id=request.user.id, type=UsersConnect.PLUS)
    }
    users = UserReadSerializer(User.objects_.filter(id__in=liked_user_ids & liking_user_ids), many=True).data
    for user in users:
        if str(request.user.id) <= str(user['id']):
            user_1_id, user_2_id = request.user.id, user['id']
        else:
            user_1_id, user_2_id = user['id'], request.user.id
        messages = sorted(
            Message.objects_.filter(user_1_id=user_1_id, user_2_id=user_2_id), key=lambda elem: elem.created
        )
        user['last_message'] = None
        if messages:
            user['last_message'] = messages[-1].created
    context = {'users': users}
    return render(request, 'chat/index.html', context)


@login_required
def room(request, room_name):
    first_user_id, second_user_id = list(map(int, room_name.split('_')))
    messages = sorted(Message.objects_.filter(
        user_1_id=first_user_id, user_2_id=second_user_id
    ), key=lambda elem: elem.created)
    if request.user.id == first_user_id:
        try:
            interlocutor = User.objects_.filter(id=second_user_id)[0]
        except Exception:
            raise Http404(f"Пользователя с данным id ({second_user_id}) не существует в базе")
    elif request.user.id == second_user_id:
        try:
            interlocutor = User.objects_.filter(id=first_user_id)[0]
        except Exception:
            raise Http404(f"Пользователя с данным id ({first_user_id}) не существует в базе")
    else:
        raise Http404(f"Вы не имеете доступа к данному чату")
    chat_exists = True
    if not (
            UsersConnect.objects_.filter(user_1_id=request.user.id, user_2_id=interlocutor.id, type=UsersConnect.PLUS)
            and
            UsersConnect.objects_.filter(user_1_id=interlocutor.id, user_2_id=request.user.id, type=UsersConnect.PLUS)
           ):
        chat_exists = False
    if str(first_user_id) > str(second_user_id):
        chat_exists = False
    context = {
        'room_name': room_name,
        'messages': messages,
        'interlocutor': interlocutor,
        'chat_exists': chat_exists
    }
    return render(request, 'chat/room.html', context)
