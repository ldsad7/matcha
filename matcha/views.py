import requests
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.gis.geoip2 import GeoIP2

from .models import (
    Tag, User, UserTag, UserPhoto, UsersConnect,
)
from .serializers import (
    TagSerializer, UserSerializer, UserTagSerializer, UserPhotoSerializer, UserReadSerializer,
    UsersConnectSerializer, UsersConnectReadSerializer,
)
from .filters import UserFilter

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
def tag_list(request):
    return common_list(request, Tag, TagSerializer, TagSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def tag_detail(request, id):
    return common_detail(request, Tag, TagSerializer, TagSerializer, id)


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = UserFilter
    ordering_fields = ('first_name', 'second_name')

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        user_tags = {user_tag.tag.name for user_tag in UserTag.objects.filter(user=request.user)}
        new_tags = {tag.strip().strip('#') for tag in request.data.get('tags') if tag.strip().strip('#')}

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        g = GeoIP2()
        ip = '205.186.163.125'
        # print(g.country(ip))
        # print(g.city(ip))
        print(g.lat_lon(ip))

        UserTag.objects.filter(tag__name__in=user_tags - new_tags).delete()

        UserTag.objects.bulk_create([
            UserTag(
                user=request.user,
                tag=Tag.objects.get_or_create(name=tag_name)[0]
            )
            for tag_name in new_tags - user_tags
        ])

        return super().update(request, *args, **kwargs)

    @action(detail=True)
    def liking(self, request, *args, **kwargs):
        """
        returns those users that liked current user
        """
        user = self.get_object()
        users = [
            user_connect.user_1
            for user_connect in UsersConnect.objects.filter(user_2=user)
        ]
        return Response(UserReadSerializer(users, many=True).data)

    @action(detail=True)
    def liked(self, request, *args, **kwargs):
        """
        returns those users whom current user likes
        """
        user = self.get_object()
        users = [
            user_connect.user_2
            for user_connect in UsersConnect.objects.filter(user_1=user)
        ]
        return Response(UserReadSerializer(users, many=True).data)


class UserTagViewSet(ModelViewSet):
    serializer_class = UserTagSerializer
    queryset = UserTag.objects.all()


class UserPhotoViewSet(ModelViewSet):
    serializer_class = UserPhotoSerializer
    queryset = UserPhoto.objects.all()


class UsersConnectViewSet(ModelViewSet):
    serializer_class = UsersConnectSerializer
    queryset = UsersConnect.objects.all()


@api_view(['GET', 'POST'])
def users_connects_list(request):
    return common_list(request, UsersConnect, UsersConnectSerializer, UsersConnectReadSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def users_connects_detail(request, id):
    return common_detail(request, UsersConnect, UsersConnectSerializer, UsersConnectReadSerializer, id)


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
