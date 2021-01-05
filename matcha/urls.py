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
    path('users/<int:id>/liking/', views.user_liking, name='user_linkng'),
    path('users/<int:id>/liked/', views.user_liked, name='user_liked'),
    path('tags/', views.tag_list, name='tags'),
    path('tags/<int:id>/', views.tag_detail, name='tags'),
    path('user_connects/', views.users_connects_list, name='user_connects'),
    path('user_connects/<int:id>/', views.users_connects_detail, name='user_connects'),
    path('user_fakes/', views.users_fakes_list, name='user_fakes'),
    path('user_fakes/<int:id>/', views.users_fakes_detail, name='user_fakes'),
    path('user_blacklists/', views.users_blacklists_list, name='user_blacklists'),
    path('user_blacklists/<int:id>/', views.users_blacklists_detail, name='user_blacklists'),
    path('user_ratings/', views.users_ratings_list, name='user_ratings'),
    path('user_ratings/<int:id>/', views.users_ratings_detail, name='user_ratings'),
    path('user_tags/', views.user_tags_list, name='user_tags'),
    path('user_tags/<int:id>/', views.user_tags_detail, name='user_tags'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/read/', views.read_notifications, name='notifications'),
    path('notifications/<int:id>/', views.notifications_detail, name='notifications'),
    path('user_photos/', views.user_photos_list, name='user_photos'),
    path('user_photos/update_main/', views.user_photos_update_main, name='user_photos'),
    path('user_photos/<int:id>/update/', views.user_photos_update, name='user_photos'),
    path('user_photos/<int:id>/', views.user_photos_detail, name='user_photos'),
    path('messages/', views.messages_list, name='messages'),
    path('messages/<int:id>/', views.messages_detail, name='messages'),

    path('location/', views.get_locations, name='location'),
]
