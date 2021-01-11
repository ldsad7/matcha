from datetime import datetime

import pytz
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from rest_framework.exceptions import PermissionDenied

from dating_site.settings import PAGE_SIZE
from matcha.filters import filter_name
from matcha.models import UsersConnect, User, Message
from matcha.serializers import UserReadSerializer, ShortUserSerializer, MessageSerializer
from matcha.tasks import ignore_only_blocked_and_faked_users_bidir


@login_required
@never_cache
def index(request):
    liked_user_ids = {
        user_connect.user_2_id
        for user_connect in UsersConnect.objects_.filter(user_1_id=request.user.id, type=UsersConnect.PLUS)
    }
    liking_user_ids = {
        user_connect.user_1_id
        for user_connect in UsersConnect.objects_.filter(user_2_id=request.user.id, type=UsersConnect.PLUS)
    }
    users = User.objects_.filter(id__in=liked_user_ids & liking_user_ids)
    name = request.GET.get('name')
    if name is not None:
        users = filter_name(users, name)

    users = ignore_only_blocked_and_faked_users_bidir(users, request.user.id)

    users = UserReadSerializer(users, many=True).data
    for user in users:
        if str(request.user.id) <= str(user['id']):
            user_1_id, user_2_id = request.user.id, user['id']
        else:
            user_1_id, user_2_id = user['id'], request.user.id
        messages = sorted(
            Message.objects_.filter(user_1_id=user_1_id, user_2_id=user_2_id), key=lambda elem: elem.created
        )
        user['last_message'] = 'Нет сообщений'
        if messages:
            user['last_message'] = messages[-1].created.replace(tzinfo=pytz.UTC)

    try:
        page = int(float(request.GET.get('page', 1)))
    except ValueError as e:
        print(f"ValueError happened: {e}")
        page = 1
    page_size = PAGE_SIZE * 2
    max_page = max((len(users) + page_size - 1) // page_size, 1)
    if not (1 <= page <= max_page):
        raise Http404(f"Страницы с данным номером ({page}) не существует")
    context = {
        'users': sorted(
            users,
            key=lambda elem: datetime.min.replace(tzinfo=pytz.UTC)
                if isinstance(elem['last_message'], str) else elem['last_message'],
            reverse=True
        )[(page - 1) * 2 * page_size:page * page_size],
        'page': page,
        'max_page': max_page
    }
    return render(request, 'chat/index.html', context)


@login_required
@never_cache
def room(request, room_name):
    try:
        first_user_id, second_user_id = list(map(int, room_name.split('_')))
    except Exception:
        raise PermissionDenied(f"Вы не имеете доступа к данному чату")
    messages = sorted(Message.objects_.filter(
        user_1_id=first_user_id, user_2_id=second_user_id
    ), key=lambda elem: elem.created)
    for message in messages:
        message.created = message.created.replace(tzinfo=pytz.UTC)
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
        raise PermissionDenied(f"Вы не имеете доступа к данному чату")
    chat_exists = True
    if not (
            UsersConnect.objects_.filter(user_1_id=request.user.id, user_2_id=interlocutor.id, type=UsersConnect.PLUS)
            and
            UsersConnect.objects_.filter(user_1_id=interlocutor.id, user_2_id=request.user.id, type=UsersConnect.PLUS)
    ):
        chat_exists = False
    if str(first_user_id) > str(second_user_id):
        chat_exists = False
    if not chat_exists:
        raise PermissionDenied(f"Вы не имеете доступа к данному чату")
    context = {
        'room_name': room_name,
        'messages': messages,
        'chat_exists': chat_exists,
        'interlocutor': ShortUserSerializer(interlocutor).data
    }
    return render(request, 'chat/room.html', context)
