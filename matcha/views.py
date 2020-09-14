import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.gis.geoip2 import GeoIP2

from .models import (
    Tag, User, UserTag, UserPhoto, UsersConnect,
)
from .serializers import (
    TagSerializer, UserSerializer, UserPhotoSerializer, UserReadSerializer,
    UsersConnectSerializer, UsersConnectReadSerializer, UserTagSerializer, UserTagReadSerializer,
    UserPhotoReadSerializer)
from .filters import filter_age, filter_rating, filter_location, filter_tags

from django.template import loader
from django.http import HttpResponse, JsonResponse


def common_list(request, model, model_serializer, model_read_serializer):
    if request.method == 'GET':
        objs = model.objects_.all()
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
    return common_detail(request, User, UserSerializer, UserReadSerializer, id)


@api_view(['GET', 'POST'])
def tag_list(request):
    return common_list(request, Tag, TagSerializer, TagSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def tag_detail(request, id):
    return common_detail(request, Tag, TagSerializer, TagSerializer, id)


@api_view(['GET'])
def user_liking(request, id):
    """
    returns those users that liked current user
    """

    user = User.objects_.get(id=id)
    users = [
        user_connect.user_1
        for user_connect in UsersConnect.objects_.filter(user_2_id=user.id)
    ]
    return Response(UserReadSerializer(users, many=True).data)


@api_view(['GET'])
def user_liked(request, id):
    """
    returns those users whom current user likes
    """

    user = User.objects_.get(id=id)
    users = [
        user_connect.user_2
        for user_connect in UsersConnect.objects_.filter(user_1_id=user.id)
    ]
    return Response(UserReadSerializer(users, many=True).data)


@api_view(['GET', 'POST'])
def user_tags_list(request):
    return common_list(request, UserTag, UserTagSerializer, UserTagReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def user_tags_detail(request, id):
    if request.method in ['PUT', 'PATCH']:
        user_tags = {user_tag.tag.name for user_tag in UserTag.objects_.filter(user=request.user)}
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

        UserTag.objects_.filter(tag__name__in=user_tags - new_tags).delete()

        for tag_name in new_tags - user_tags:
            UserTag(user=request.user, tag=Tag.objects_.get_or_create(name=tag_name)[0]).save()
    return common_detail(request, UserTag, UserTagSerializer, UserTagReadSerializer, id)


@api_view(['GET', 'POST'])
def user_photos_list(request):
    return common_list(request, UserPhoto, UserPhotoSerializer, UserPhotoReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def user_photos_detail(request, id):
    return common_detail(request, UserPhoto, UserPhotoSerializer, UserPhotoReadSerializer, id)


@api_view(['GET', 'POST'])
def users_connects_list(request):
    return common_list(request, UsersConnect, UsersConnectSerializer, UsersConnectReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def users_connects_detail(request, id):
    return common_detail(request, UsersConnect, UsersConnectSerializer, UsersConnectReadSerializer, id)


# Additional functions


def index(request):
    template = loader.get_template('index.html')
    context = {'users': UserReadSerializer(User.objects.all(), many=True).data}
    return HttpResponse(template.render(context, request))


def search(request):
    template = loader.get_template('search.html')
    context = {'users': UserReadSerializer(User.objects.all(), many=True).data}
    return HttpResponse(template.render(context, request))


def profile(request):
    template = loader.get_template('profile.html')
    context = UserReadSerializer(request.user).data
    return HttpResponse(template.render(context, request))


def get_locations(request):
    return JsonResponse(requests.get(
        "https://www.avito.ru/web/1/slocations?locationId=637640&limit=10&q=" +
        request.GET['value']
    ).json())
