from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

api_router = DefaultRouter()
# api_router.register('tags', TagViewSet, 'tags')
api_router.register('users', views.UserViewSet, 'users')
api_router.register('user_tags', views.UserTagViewSet, 'user_tags')
api_router.register('user_photos', views.UserPhotoViewSet, 'user_photos')
# api_router.register('user_connects', views.UsersConnectViewSet, 'user_connects')


urlpatterns = [
    path('', include(api_router.urls)),
    path('tags/', views.tag_list, name='tags'),
    path('tags/<int:id>/', views.tag_detail, name='tags'),
    path('user_connects/', views.users_connects_list, name='tags'),
    path('user_connects/<int:id>/', views.users_connects_detail, name='tags'),

    path('location/', views.get_locations, name='location'),
]
