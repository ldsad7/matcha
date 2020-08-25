from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet, UserViewSet, UserTagViewSet, UserPhotoViewSet
)

api_router = DefaultRouter()
api_router.register('tags', TagViewSet, 'tags')
api_router.register('users', UserViewSet, 'users')
api_router.register('user_tags', UserTagViewSet, 'user_tags')
api_router.register('user_photos', UserPhotoViewSet, 'user_photos')

urlpatterns = [
    path('', include(api_router.urls)),
]
