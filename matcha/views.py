from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet

from .models import (
    Tag, User, UserTag, UserPhoto
)
from .serializers import (
    TagSerializer, UserSerializer, UserTagSerializer, UserPhotoSerializer
)


## что я добавил:
## -->
from django.template import loader
from django.http import HttpResponse
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


class UserTagViewSet(ModelViewSet):
    serializer_class = UserTagSerializer
    queryset = UserTag.objects.all()


class UserPhotoViewSet(ModelViewSet):
    serializer_class = UserPhotoSerializer
    queryset = UserPhoto.objects.all()
