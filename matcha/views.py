import uuid

import requests
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.gis.geoip2 import GeoIP2

from .models import (
    Tag, User, UserTag, UserPhoto, UsersConnect,
    UsersFake, UsersBlackList, Notification)
from .serializers import (
    TagSerializer, UserSerializer, UserPhotoSerializer, UserReadSerializer,
    UsersConnectSerializer, UsersConnectReadSerializer, UserTagSerializer, UserTagReadSerializer,
    UserPhotoReadSerializer,
    UsersFakeSerializer, UsersFakeReadSerializer, UsersBlackListSerializer, UsersBlackListReadSerializer,
    NotificationSerializer, NotificationReadSerializer)
from .filters import filter_age, filter_rating, filter_location, filter_tags, filter_timestamp

from django.template import loader
from django.http import HttpResponse, JsonResponse, Http404

MINUS = '-'


def order_by(objs, field):
    starts_with_minus = field.startswith(MINUS)
    objs = sorted(objs, key=lambda elem: getattr(elem, field.strip(MINUS)))
    if starts_with_minus:
        objs = objs[::-1]
    return objs


def common_list(request, model, model_serializer, model_read_serializer, order_by_field=None):
    if request.method == 'GET':
        objs = model.objects_.all()
        if order_by_field is not None:
            objs = order_by(objs, order_by_field)
        serializer = model_read_serializer(objs, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = model_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        raise ValueError("Invalid request")


def common_detail(request, model, model_serializer, model_read_serializer, id_):
    obj = model.objects_.get(id=id_)
    if obj is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = model_read_serializer(obj)
        return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        serializer = model_serializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        obj.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
    else:
        raise ValueError("Invalid request")


@api_view(['GET', 'POST'])
def user_list(request):
    if request.method == 'GET':
        objs = User.objects_.all()
        for query_param, value in request.query_params.items():
            if query_param == 'age':
                objs = filter_age(objs, value, User)
            elif query_param == 'rating':
                objs = filter_rating(objs, value, User)
            elif query_param == 'location':
                objs = filter_location(objs, value, User)
            elif query_param == 'tags':
                objs = filter_tags(objs, value, User)
        serializer = UserReadSerializer(objs, many=True)
        return Response(serializer.data)
    return common_list(request, User, UserSerializer, UserReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def user_detail(request, id):
    if request.method in ['PUT', 'PATCH']:
        user_tags = {user_tag.tag.name for user_tag in UserTag.objects_.filter(user_id=request.user.id)}
        new_tags = {tag.strip().strip('#') for tag in request.data.get('tags') if tag.strip().strip('#')}

        # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        # if x_forwarded_for:
        #     ip = x_forwarded_for.split(',')[0]
        # else:
        #     ip = request.META.get('REMOTE_ADDR')
        # g = GeoIP2()
        # ip = '205.186.163.125'
        # print(g.country(ip))
        # print(g.city(ip))
        # print(g.lat_lon(ip))

        tag_ids = [obj.id for obj in Tag.objects_.filter(name__in=user_tags - new_tags)]
        for obj in UserTag.objects_.filter(tag_id__in=tag_ids):
            obj.delete()

        for tag_name in new_tags - user_tags:
            if not tag_name:
                continue
            if not Tag.objects_.filter(name=tag_name):
                Tag(name=tag_name).save()
            tag_obj = Tag.objects_.filter(name=tag_name)[0]
            UserTag(user_id=request.user.id, tag_id=tag_obj.id).save()
    return common_detail(request, User, UserSerializer, UserReadSerializer, id)


@api_view(['GET', 'POST'])
def tag_list(request):
    return common_list(request, Tag, TagSerializer, TagSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def tag_detail(request, id):
    return common_detail(request, Tag, TagSerializer, TagSerializer, id)


def liking(id):
    """
    returns those users that liked current user
    """

    user = User.objects_.get(id=id)
    users = [
        user_connect.user_1
        for user_connect in UsersConnect.objects_.filter(user_2_id=user.id)
    ]
    data = UserReadSerializer(users, many=True).data
    for user in data:
        user_connects = UsersConnect.objects_.filter(
            user_1_id=id, user_2_id=user['id']
        )
        if user_connects:
            user['liked_back'] = user_connects[0].type == UsersConnect.PLUS
            user['users_connect_id'] = user_connects[0].id
    return data


@api_view(['GET'])
def user_liking(request, id):
    return Response(liking(id))


def liked(id):
    """
    returns those users whom current user likes
    """

    user = User.objects_.get(id=id)
    users = [
        user_connect.user_2
        for user_connect in UsersConnect.objects_.filter(user_1_id=user.id)
    ]
    return UserReadSerializer(users, many=True).data


@api_view(['GET'])
def user_liked(request, id):
    return Response(liked(id))


@api_view(['GET', 'POST'])
def user_tags_list(request):
    return common_list(request, UserTag, UserTagSerializer, UserTagReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def user_tags_detail(request, id):
    return common_detail(request, UserTag, UserTagSerializer, UserTagReadSerializer, id)


@api_view(['GET', 'POST'])
def user_photos_list(request):
    if request.method == 'POST':
        uuid1 = uuid.uuid1()
        file_name = f'.{settings.MEDIA_URL}{UserPhoto.image.field.upload_to}tmp_{request.data["user_id"]}_{uuid1}.jpg'
        image = request.data.get('image')
        if image:
            file = image.file.read()
            request.data['image'] = f'tmp_{request.data["user_id"]}_{uuid1}.jpg'
        serializer = UserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            if image:
                with open(file_name, 'wb') as f:
                    f.write(file)
            serializer.save()
            serialized_data = serializer.data
            if image:
                serialized_data['image'] = serialized_data['image'].replace('/media/', '/media/images/')
            return Response(serialized_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return common_list(request, UserPhoto, UserPhotoSerializer, UserPhotoReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def user_photos_detail(request, id):
    return common_detail(request, UserPhoto, UserPhotoSerializer, UserPhotoReadSerializer, id)


@api_view(['GET', 'POST'])
def users_connects_list(request):
    return common_list(
        request, UsersConnect, UsersConnectSerializer, UsersConnectReadSerializer,
        order_by_field='-created'
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def users_connects_detail(request, id):
    return common_detail(
        request, UsersConnect, UsersConnectSerializer, UsersConnectReadSerializer, id
    )


@api_view(['GET', 'POST'])
def users_fakes_list(request):
    return common_list(request, UsersFake, UsersFakeSerializer, UsersFakeReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def users_fakes_detail(request, id):
    return common_detail(request, UsersFake, UsersFakeSerializer, UsersFakeReadSerializer, id)


@api_view(['GET', 'POST'])
def users_blacklists_list(request):
    return common_list(
        request, UsersBlackList, UsersBlackListSerializer, UsersBlackListReadSerializer
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def users_blacklists_detail(request, id):
    return common_detail(
        request, UsersBlackList, UsersBlackListSerializer, UsersBlackListReadSerializer, id
    )


@api_view(['GET', 'POST'])
def notifications_list(request):
    if request.method == 'GET':
        objs = Notification.objects_.all()
        for query_param, value in request.query_params.items():
            if query_param == 'created':
                try:
                    value = int(value)
                except ValueError:
                    raise Http404(f"В базе нет notification-а с данным id ({value})")
                objs = filter_timestamp(objs, value)
        objs = order_by(objs, '-created')
        serializer = NotificationReadSerializer(objs, many=True)
        return Response(serializer.data)
    return common_list(request, Notification, NotificationSerializer, NotificationReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def notifications_detail(request, id):
    return common_detail(
        request, Notification, NotificationSerializer, NotificationReadSerializer, id
    )


# Additional functions


def index(request):
    template = loader.get_template('index.html')
    context = {
        'users': UserReadSerializer(User.objects.all(), many=True).data,
        'user': request.user
    }
    return HttpResponse(template.render(context, request))


def search(request):
    template = loader.get_template('search.html')
    context = {
        'users': UserReadSerializer(User.objects.all(), many=True).data,
        'user': request.user
    }
    return HttpResponse(template.render(context, request))


def profile(request):
    template = loader.get_template('profile.html')
    context = UserReadSerializer(request.user).data
    context['user'] = request.user
    return HttpResponse(template.render(context, request))


def user_profile(request, id):
    template = loader.get_template('user_profile.html')
    user = User.objects_.get(id=id)
    if user is not None:
        context = UserReadSerializer(user).data
    else:
        raise Http404(f"Пользователя с данным id ({id}) не существует в базе")
    context['user'] = request.user
    return HttpResponse(template.render(context, request))


def connections(request):
    template = loader.get_template('connections.html')
    context = {
        'users': liking(request.user.id),
        'user': request.user
    }
    # UserReadSerializer(User.objects.all(), many=True).data,
    return HttpResponse(template.render(context, request))


def get_locations(request):
    return JsonResponse(requests.get(
        "https://www.avito.ru/web/1/slocations?locationId=637640&limit=10&q=" +
        request.GET['value']
    ).json())
