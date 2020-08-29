from django.contrib import admin
from django.urls import path, include

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
    path('api/v1/', include('matcha.urls')),
    path(
        'api/v1/docs/', schema_view.with_ui(cache_timeout=0), name='API'
    ),
    path('accounts/', include('registration.backends.default.urls')),
    path('accounts/profile/', views.profile, name='profile'),
]
