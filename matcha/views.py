import time
import uuid

import mpu
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.template import loader
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from dating_site.settings import PAGE_SIZE, MEDIA_PREFIX
from .filters import filter_age, filter_rating, filter_location, filter_tags, filter_timestamp
from .models import (
    Tag, User, UserTag, UserPhoto, UsersConnect, UsersFake, UsersBlackList, Notification, Message,
    UsersRating)
from .serializers import (
    TagSerializer, UserSerializer, UserPhotoSerializer, UserReadSerializer, UsersConnectSerializer,
    UsersConnectReadSerializer, UserTagSerializer, UserTagReadSerializer, UserPhotoReadSerializer,
    UsersFakeSerializer, UsersFakeReadSerializer, UsersBlackListSerializer,
    UsersBlackListReadSerializer, NotificationSerializer, NotificationReadSerializer,
    MessageSerializer, MessageReadSerializer, UsersRatingSerializer, UsersRatingReadSerializer,
    ShortUserSerializer)
from .tasks import ignore_false_users, ignore_by_orientation_and_gender

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
        # return ListCreateAPIView.get_paginated_response(data=serializer.data)
    elif request.method == 'POST':
        serializer = model_serializer(data=request.data, many=True)
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
        return Response(UserReadSerializer(objs, many=True).data)
    return common_list(request, User, UserSerializer, UserReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def user_detail(request, id):
    if request.method in ['PUT', 'PATCH']:
        user_tags = {user_tag.tag.name for user_tag in UserTag.objects_.filter(user_id=request.user.id)}
        new_tags = {tag.strip().strip('#') for tag in request.data.get('tags') if tag.strip().strip('#')}
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
        if not user_connects:
            UsersConnect(
                user_1_id=id,
                user_2_id=user['id'],
                type=UsersConnect.MINUS
            ).save()
            user_connects = UsersConnect.objects_.filter(
                user_1_id=id, user_2_id=user['id']
            )

        user['liked_back'] = user_connects[0].type == UsersConnect.PLUS
        user['users_connect_id'] = user_connects[0].id

    return data


@api_view(['GET'])
def user_liking(request, id):
    return Response(liking(id))


@api_view(['PATCH'])
def user_photos_update_main(request):
    image = request.data.get('image')
    new_main = request.data.get('main')
    # print(f'user_photos_update_main: image: {image}, new_main: {new_main}')
    if image.startswith(f'/{MEDIA_PREFIX}/'):
        image = image[len(f'/{MEDIA_PREFIX}/'):]
    user_photos = UserPhoto.objects_.filter(image=image)
    if user_photos:
        user_photos[0].main = new_main
        user_photos[0].save()
    return Response({'result': 'SUCCESS'})


@api_view(['PATCH'])
def user_photos_update(request, id):
    initial_images = set(request.data.get('initial_images'))
    initial_images = {
        image[len(f'/{MEDIA_PREFIX}/'):] if image.startswith(f'/{MEDIA_PREFIX}/') else image
        for image in initial_images
    }
    images = set(request.data.get('images'))
    images = {
        image[len(f'/{MEDIA_PREFIX}/'):] if image.startswith(f'/{MEDIA_PREFIX}/') else image
        for image in images
    }
    to_delete = UserPhoto.objects_.filter(user_id=id, image__in=initial_images - images)
    # print(f"user_photos_update: initial_images: {initial_images}, images: {images}, to_delete: {to_delete}")
    for image in to_delete:
        image.delete()
    return Response({'result': 'SUCCESS'})


@api_view(['PATCH'])
def read_notifications(request):
    ids = request.data.get('ids')
    if ids is not None:
        notifications = Notification.objects_.filter(id__in=ids.split(','), user_2_id=request.user.id)
        for notification in notifications:
            notification.was_read = True
            notification.save()
        return Response({'result': 'OK'})
    return Response({'result': 'FAIL'})


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
                serialized_data['image'] = serialized_data['image'].replace('/media/', f'/{MEDIA_PREFIX}/')
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
def users_ratings_list(request):
    return common_list(
        request, UsersRating, UsersRatingSerializer, UsersRatingReadSerializer,
        order_by_field='-created'
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def users_ratings_detail(request, id):
    return common_detail(
        request, UsersRating, UsersRatingSerializer, UsersRatingReadSerializer, id
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
        objs = Notification.objects_.filter(user_2_id=request.user.id, was_read=0)
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


@api_view(['GET', 'POST'])
def messages_list(request):
    return common_list(request, Message, MessageSerializer, MessageReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def messages_detail(request, id):
    return common_detail(request, Message, MessageSerializer, MessageReadSerializer, id)


####################################
# Additional functions
####################################


# class Timer:
#     def __enter__(self):
#         self.start = time.clock()
#         return self
#
#     def __exit__(self, *args):
#         self.end = time.clock()
#         self.interval = self.end - self.start
#         print(f"time interval: {self.interval}")


def index(request):
    template = loader.get_template('index.html')
    users = User.objects_.all()
    try:
        page = int(float(request.GET.get('page', 1)))
    except ValueError as e:
        print(f"ValueError happened: {e}")
        page = 1
    user_id = request.user.id
    if user_id is not None:
        user_ratings = sorted(
            UsersRating.objects_.filter(user_2_id=user_id), key=lambda elem: -elem.rating
        )
        if user_ratings:
            correct_ids = [user_rating.user_1_id for user_rating in user_ratings]
            users = [inner_user for inner_user in users if inner_user.id in correct_ids]
        else:
            users = ignore_false_users(users, user_id)
            users = ignore_by_orientation_and_gender(users, request.user)
    max_page = max((len(users) + PAGE_SIZE - 1) // PAGE_SIZE, 1)
    if not(1 <= page <= max_page):
        raise Http404(f"Страницы с данным номером ({page}) не существует")
    context = {
        'users': ShortUserSerializer(users[(page - 1) * PAGE_SIZE:page * PAGE_SIZE], many=True).data,
        'page': page,
        'max_page': max_page
    }
    return HttpResponse(template.render(context, request))


@login_required
def search(request):
    template = loader.get_template('search.html')
    context = {
        'users': UserReadSerializer(User.objects.all(), many=True).data
    }
    return HttpResponse(template.render(context, request))


@login_required
def profile(request):
    template = loader.get_template('profile.html')
    context = UserReadSerializer(request.user).data
    return HttpResponse(template.render(context, request))


@login_required
def user_profile(request, id):
    template = loader.get_template('user_profile.html')
    user = User.objects_.get(id=id)
    if user is not None:
        context = UserReadSerializer(user).data
    else:
        raise Http404(f"Пользователя с данным id ({id}) не существует в базе")
    print(f'context: {context}')
    return HttpResponse(template.render(context, request))


@login_required
def connections(request):
    template = loader.get_template('connections.html')
    context = {
        'users': liking(request.user.id)
    }
    # UserReadSerializer(User.objects.all(), many=True).data,
    return HttpResponse(template.render(context, request))


def get_locations(request):
    return JsonResponse(requests.get(
        "https://www.avito.ru/web/1/slocations?locationId=637640&limit=10&q=" +
        request.GET['value']
    ).json())
