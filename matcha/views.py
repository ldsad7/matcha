import requests
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.gis.geoip2 import GeoIP2

from .models import (
    Tag, User, UserTag, UserPhoto, UsersConnect,
)
from .serializers import (
    TagSerializer, UserSerializer, UserTagSerializer, UserPhotoSerializer, UserReadSerializer,
    UsersConnectSerializer,
)
from .filters import UserFilter


## что я добавил:
## -->
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from uuid import uuid4 as randID

def index(request):
    template = loader.get_template('test_upload.html')
    context = {'1' : 'true'} # just for example
    return HttpResponse(template.render(context, request))

def handle_uploaded_file(f, name):
    with open('media/images/' + name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@csrf_exempt
def images(request):
    ''' gets image from Ajax, generates random name, uploads file in media/images and returns src of this img '''
    if request.method == 'POST':
        randName = randID().__str__() + '.' + request.FILES['image'].__str__().split('.')[-1]
        handle_uploaded_file(request.FILES['image'], randName)
    return HttpResponse(randName)
##  <--


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


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
