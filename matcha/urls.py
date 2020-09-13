from django.urls import path, include
# from rest_framework.routers import DefaultRouter

from . import views

# api_router = DefaultRouter()
# api_router.register('tags', TagViewSet, 'tags')
# api_router.register('users', views.UserViewSet, 'users')
# api_router.register('user_tags', views.UserTagViewSet, 'user_tags')
# api_router.register('user_photos', views.UserPhotoViewSet, 'user_photos')
# api_router.register('user_connects', views.UsersConnectViewSet, 'user_connects')


urlpatterns = [
    # path('', include(api_router.urls)),
    path('users/', views.user_list, name='users'),
    path('users/<int:id>/', views.user_detail, name='users'),
    path('tags/', views.tag_list, name='tags'),
    path('tags/<int:id>/', views.tag_detail, name='tags'),
    path('user_connects/', views.users_connects_list, name='user_connects'),
    path('user_connects/<int:id>/', views.users_connects_detail, name='user_connects'),
    path('user_tags/', views.user_tags_list, name='user_tags'),
    path('user_tags/<int:id>/', views.user_tags_detail, name='user_tags'),
    path('user_photos/', views.user_photos_list, name='user_photos'),
    path('user_photos/<int:id>/', views.user_photos_detail, name='user_photos'),

    path('location/', views.get_locations, name='location'),
]
