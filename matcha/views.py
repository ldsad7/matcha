import uuid
from datetime import date, datetime, timedelta

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse, JsonResponse, Http404
from django.template import loader
from django.views.decorators.cache import never_cache
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from dating_site.settings import PAGE_SIZE, MEDIA_PREFIX, MAX_AGE, MAX_RATING
from .filters import filter_name
from .models import (
    Tag, User, UserTag, UserPhoto, UsersConnect, UsersFake, UsersBlackList, Notification, Message,
    UsersRating)
from .serializers import (
    TagSerializer, UserSerializer, UserPhotoSerializer, UserReadSerializer, UsersConnectSerializer,
    UsersConnectReadSerializer, UserTagSerializer, UserTagReadSerializer, UserPhotoReadSerializer,
    UsersFakeSerializer, UsersFakeReadSerializer, UsersBlackListSerializer,
    UsersBlackListReadSerializer, NotificationSerializer, NotificationReadSerializer,
    MessageSerializer, MessageReadSerializer, UsersRatingSerializer, UsersRatingReadSerializer,
    ShortUserSerializer, ShortNotificationReadSerializer)
from .tasks import ignore_false_users, ignore_by_orientation_and_gender, ignore_only_blocked_and_faked_users_bidir, \
    ignore_only_blocked_and_faked_users_onedir, update_rating

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
        serializer = model_serializer(data=request.data)
        serializer.context.update({
            'user_id': request.user.id
        })
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
        serializer.context.update({
            'user_id': request.user.id
        })
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
@never_cache
@login_required
def user_list(request):
    if request.method == 'GET':
        return Response(ShortUserSerializer(User.objects_.all(), many=True).data)
    return common_list(request, User, UserSerializer, UserReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@never_cache
@login_required
def user_detail(request, id):
    try:
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
    except Exception as e:
        raise SuspiciousOperation(e)
    return common_detail(request, User, UserSerializer, UserReadSerializer, id)


@api_view(['GET', 'POST'])
@never_cache
@login_required
def tag_list(request):
    return common_list(request, Tag, TagSerializer, TagSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@never_cache
@login_required
def tag_detail(request, id):
    return common_detail(request, Tag, TagSerializer, TagSerializer, id)


def liking(user_id):
    """
    returns those users that liked current user
    """

    user = User.objects_.get(id=user_id)
    users = [
        user_connect.user_1
        for user_connect in UsersConnect.objects_.filter(user_2_id=user.id)
    ]
    users = ignore_only_blocked_and_faked_users_onedir(users, user_id)
    data = ShortUserSerializer(users, many=True).data
    for user in data:
        user_connects = UsersConnect.objects_.filter(
            user_1_id=user_id, user_2_id=user['id']
        )
        if not user_connects:
            UsersConnect(
                user_1_id=user_id,
                user_2_id=user['id'],
                type=UsersConnect.MINUS
            ).save()
            user_connects = UsersConnect.objects_.filter(
                user_1_id=user_id, user_2_id=user['id']
            )
        user['liked_back'] = user_connects[0].type == UsersConnect.PLUS
        user['users_connect_id'] = user_connects[0].id
        user['created_connect'] = user_connects[0].created

    return sorted(data, key=lambda elem: elem['created_connect'])[::-1]


@api_view(['GET'])
@never_cache
@login_required
def user_liking(request, id):
    return Response(liking(id))


@api_view(['PATCH'])
@never_cache
@login_required
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
@never_cache
@login_required
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
@never_cache
@login_required
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
@never_cache
@login_required
def user_liked(request, id):
    return Response(liked(id))


@api_view(['GET', 'POST'])
@never_cache
@login_required
def user_tags_list(request):
    return common_list(request, UserTag, UserTagSerializer, UserTagReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@never_cache
@login_required
def user_tags_detail(request, id):
    return common_detail(request, UserTag, UserTagSerializer, UserTagReadSerializer, id)


@api_view(['GET', 'POST'])
@never_cache
@login_required
def user_photos_list(request):
    if request.method == 'POST':
        uuid1 = uuid.uuid1()
        file_name = f'.{settings.MEDIA_URL}{UserPhoto.image.field.upload_to}tmp_{request.data["user_id"]}_{uuid1}.jpg'
        image = request.data.get('image')
        if image:
            file = image.file.read()
            request.data['image'] = f'tmp_{request.data["user_id"]}_{uuid1}.jpg'
        serializer = UserPhotoSerializer(data=request.data)
        serializer.context.update({
            'user_id': request.user.id
        })
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
@never_cache
@login_required
def user_photos_detail(request, id):
    return common_detail(request, UserPhoto, UserPhotoSerializer, UserPhotoReadSerializer, id)


@api_view(['GET', 'POST'])
@never_cache
@login_required
def users_connects_list(request):
    return common_list(
        request, UsersConnect, UsersConnectSerializer, UsersConnectReadSerializer,
        order_by_field='-created'
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@never_cache
@login_required
def users_connects_detail(request, id):
    return common_detail(
        request, UsersConnect, UsersConnectSerializer, UsersConnectReadSerializer, id
    )


@api_view(['GET', 'POST'])
@never_cache
@login_required
def users_ratings_list(request):
    return common_list(
        request, UsersRating, UsersRatingSerializer, UsersRatingReadSerializer,
        order_by_field='-created'
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@never_cache
@login_required
def users_ratings_detail(request, id):
    return common_detail(
        request, UsersRating, UsersRatingSerializer, UsersRatingReadSerializer, id
    )


@api_view(['GET', 'POST'])
@never_cache
@login_required
def users_fakes_list(request):
    return common_list(request, UsersFake, UsersFakeSerializer, UsersFakeReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@never_cache
@login_required
def users_fakes_detail(request, id):
    return common_detail(request, UsersFake, UsersFakeSerializer, UsersFakeReadSerializer, id)


@api_view(['GET', 'POST'])
@never_cache
@login_required
def users_blacklists_list(request):
    return common_list(
        request, UsersBlackList, UsersBlackListSerializer, UsersBlackListReadSerializer
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@never_cache
@login_required
def users_blacklists_detail(request, id):
    return common_detail(
        request, UsersBlackList, UsersBlackListSerializer, UsersBlackListReadSerializer, id
    )


@api_view(['GET', 'POST'])
@never_cache
@login_required
def notifications_list(request):
    if request.method == 'GET':
        objs = Notification.objects_.filter(user_2_id=request.user.id, was_read=0)
        objs = [
            obj for obj in objs
            if not UsersBlackList.objects_.filter(user_1_id=request.user.id, user_2_id=obj.user_1_id) and
               not UsersFake.objects_.filter(user_1_id=request.user.id, user_2_id=obj.user_1_id) and
               not UsersConnect.objects_.filter(user_1_id=request.user.id, user_2_id=obj.user_1_id,
                                                type=UsersConnect.MINUS)
        ]
        # for query_param, value in request.query_params.items():
        #     if query_param == 'created':
        #         try:
        #             value = int(value)
        #         except ValueError:
        #             raise Http404(f"В базе нет notification-а с данным id ({value})")
        #         objs = filter_timestamp(objs, value)
        objs = order_by(objs, 'created')
        serializer = NotificationReadSerializer(objs, many=True)
        return Response(serializer.data)
    return common_list(request, Notification, NotificationSerializer, NotificationReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@never_cache
@login_required
def notifications_detail(request, id):
    return common_detail(
        request, Notification, NotificationSerializer, NotificationReadSerializer, id
    )


@api_view(['GET', 'POST'])
@never_cache
@login_required
def messages_list(request):
    return common_list(request, Message, MessageSerializer, MessageReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@never_cache
@login_required
def messages_detail(request, id):
    return common_detail(request, Message, MessageSerializer, MessageReadSerializer, id)


####################################
# Additional functions
####################################


def get_page(request, len_users):
    try:
        page = int(float(request.GET.get('page', 1)))
    except ValueError as e:
        print(f"ValueError happened: {e}. Setting page=1.")
        page = 1
    max_page = max((len_users + PAGE_SIZE - 1) // PAGE_SIZE, 1)
    if not (1 <= page <= max_page):
        raise Http404(f"Страницы с данным номером ({page}) не существует")
    return page, max_page


def inner_search(request):
    filters = {}

    age = request.GET.get('age')
    if age is not None:
        try:
            low, high = list(map(int, age.split(':')))
        except Exception as e:
            raise SuspiciousOperation(f'Некорректные входные значения: {age}')
        today = date.today()
        filters['date_of_birth__gte'] = date(year=today.year - high - 1, month=today.month, day=today.day)
        filters['date_of_birth__lte'] = date(year=today.year - low, month=today.month, day=today.day)

    rating = request.GET.get('rating')
    if rating is not None:
        try:
            low, high = list(map(float, rating.replace(',', '.').split(':')))
        except Exception as e:
            raise SuspiciousOperation(f"Некорректные входные значения: {rating}")
        filters['rating__gte'] = low
        filters['rating__lte'] = high

    location = request.GET.get('location')
    if location is not None:
        filters['location__icontains'] = location.lower()

    tags = request.GET.get('tags')
    if tags is not None:
        tag_names = tags.split(',')
        tag_names = [tag_name for tag_name in tag_names if tag_name]
        if tag_names:
            tag_ids = [obj.id for obj in Tag.objects_.filter(name__in=tag_names)]
            user_ids = [obj.user.id for obj in UserTag.objects_.filter(tag_id__in=tag_ids)]
            filters['id__in'] = user_ids

    if not filters:
        return User.objects_.all()
    print(f'filters: {filters}')
    users = User.objects_.filter(**filters)
    return users


def get_tags(user_id):
    user_tags = UserTag.objects_.filter(user_id=user_id)
    tags = [
        user_tag.tag.name.strip().strip('#')
        for user_tag in user_tags if user_tag.tag.name.strip().strip('#')
    ]
    return sorted(tags)


def apply_sort_filter(request, users):
    sort_filter = request.GET.get('sort')
    if sort_filter:
        parts = sort_filter.split('-')
        if len(parts) == 3:
            name, up_down, field = parts
            if name == 'sort' and up_down in ['up', 'down'] and \
                    field in ['age', 'rating', 'location', 'tags']:
                reverse = up_down == 'down'
                if field == 'tags':
                    users = sorted(users, key=lambda elem: get_tags(elem.id), reverse=reverse)
                else:
                    users = sorted(users, key=lambda elem: getattr(elem, field), reverse=reverse)
    return users


@never_cache
def index(request):
    template = loader.get_template('index.html')
    users = inner_search(request)
    user_id = request.user.id
    if user_id is not None:
        users = ignore_false_users(users, user_id)
        users = ignore_by_orientation_and_gender(users, request.user)
        user_ratings = UsersRating.objects_.filter(user_2_id=user_id)
        # if not user_ratings:
        update_rating(users, User.objects_.get(id=user_id))
        user_ratings = UsersRating.objects_.filter(user_2_id=user_id)

        # if user_ratings:
        correct_ids = [user_rating.user_1_id for user_rating in user_ratings]
        correct_ratings = [user_rating.rating for user_rating in user_ratings]
        new_users = []
        for inner_user in users:
            if inner_user.id in correct_ids:
                i = correct_ids.index(inner_user.id)
                inner_user.rating_to_user = correct_ratings[i]
                new_users.append(inner_user)
        users = sorted(new_users, key=lambda elem: -elem.rating_to_user)

    users = apply_sort_filter(request, users)

    page, max_page = get_page(request, len(users))
    context = {
        'users': ShortUserSerializer(users[(page - 1) * PAGE_SIZE:page * PAGE_SIZE], many=True).data,
        'page': page,
        'max_page': max_page,
        'max_age': MAX_AGE,
        'max_rating': MAX_RATING
    }
    return HttpResponse(template.render(context, request))


@login_required
@never_cache
def search(request):
    template = loader.get_template('search.html')

    user_id = request.user.id
    users = inner_search(request)

    name = request.GET.get('name')
    if name is not None:
        users = filter_name(users, name)

    users = ignore_only_blocked_and_faked_users_bidir(users, user_id)

    users = apply_sort_filter(request, users)

    page, max_page = get_page(request, len(users))
    context = {
        'users': ShortUserSerializer(users[(page - 1) * PAGE_SIZE:page * PAGE_SIZE], many=True).data,
        'page': page,
        'max_page': max_page,
        'max_age': MAX_AGE,
        'max_rating': MAX_RATING
    }
    return HttpResponse(template.render(context, request))


@login_required
@never_cache
def profile(request):
    template = loader.get_template('profile.html')
    context = UserReadSerializer(request.user).data
    return HttpResponse(template.render(context, request))


@login_required
@never_cache
def user_profile(request, id):
    template = loader.get_template('user_profile.html')
    user = User.objects_.get(id=id)
    if user is not None:
        context = UserReadSerializer(user).data
    else:
        raise Http404(f"Пользователя с данным id ({id}) не существует в базе")
    return HttpResponse(template.render(context, request))


@login_required
@never_cache
def connections(request):
    template = loader.get_template('connections.html')
    users = liking(request.user.id)

    page, max_page = get_page(request, len(users))
    context = {
        'users': users[(page - 1) * PAGE_SIZE:page * PAGE_SIZE],
        'page': page,
        'max_page': max_page,
        'max_age': MAX_AGE,
        'max_rating': MAX_RATING
    }

    return HttpResponse(template.render(context, request))


@login_required
@never_cache
def actions(request):
    template = loader.get_template('actions.html')
    user_id = request.user.id
    notifications_from_user = Notification.objects_.filter(
        user_1_id=user_id, created__gt=datetime.utcnow() - timedelta(days=1)
    )
    for notification in notifications_from_user:
        notification.to = False
        user = User.objects_.get(id=notification.user_2_id)
        notification.first_name = user.first_name
        notification.last_name = user.last_name
        notification.username = user.username
    notifications_to_user = Notification.objects_.filter(
        user_2_id=user_id, created__gt=datetime.utcnow() - timedelta(days=1)
    )
    for notification in notifications_to_user:
        notification.to = True
        user = User.objects_.get(id=notification.user_1_id)
        notification.first_name = user.first_name
        notification.last_name = user.last_name
        notification.username = user.username
    notifications = [*notifications_from_user, *notifications_to_user]

    name = request.GET.get('name')
    if name:
        notifications = filter_name(notifications, name)

    notifications = sorted(notifications, key=lambda elem: elem.created, reverse=True)

    page, max_page = get_page(request, len(notifications))
    context = {
        'notifications': ShortNotificationReadSerializer(
            notifications[(page - 1) * PAGE_SIZE:page * PAGE_SIZE], many=True
        ).data,
        'page': page,
        'max_page': max_page
    }
    return HttpResponse(template.render(context, request))


@login_required
def get_locations(request):
    return JsonResponse(requests.get(
        "https://www.avito.ru/web/1/slocations?locationId=637640&limit=10&q=" +
        request.GET['value']
    ).json())
