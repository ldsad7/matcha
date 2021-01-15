from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from matcha import views


schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('profiles/<int:id>/', views.user_profile, name='profiles'),
    path('api/v1/', include('matcha.urls')),
    path(
        'api/v1/docs/', schema_view.with_ui(cache_timeout=0), name='API'
    ),
    path('accounts/', include('registration.backends.default.urls')),
    path('accounts/profile/', views.profile, name='profile'),
    path('connections/', views.connections, name='connections'),
    path('actions/', views.actions, name='actions'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
