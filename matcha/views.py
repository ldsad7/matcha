# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.filters import OrderingFilter
from django.http import HttpResponse
from django.template import loader
from rest_framework.viewsets import ModelViewSet

from .models import (
    Tag, User, UserTag, UserPhoto
)
from .serializers import (
    TagSerializer, UserSerializer, UserTagSerializer, UserPhotoSerializer, UserReadSerializer
)


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class UserTagViewSet(ModelViewSet):
    serializer_class = UserTagSerializer
    queryset = UserTag.objects.all()


class UserPhotoViewSet(ModelViewSet):
    serializer_class = UserPhotoSerializer
    queryset = UserPhoto.objects.all()


def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context, request))


def search(request):
    template = loader.get_template('search.html')
    context = {}
    return HttpResponse(template.render(context, request))


def profile(request):
    # print(dir(request))
    # print(type(request.user))
    template = loader.get_template('profile.html')
    context = UserReadSerializer(request.user).data
    print(f'context: {context}')
    return HttpResponse(template.render(context, request))
