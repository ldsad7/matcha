import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = ''

DEBUG = False

ALLOWED_HOSTS = []

####################################
# Internationalization
####################################

USE_TZ = True
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True

####################################
# Application definition
####################################

INSTALLED_APPS = [
    'django.contrib.sites',
    # registration
    'registration',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # debug
    # 'debug_toolbar',

    # utility apps
    'easy_thumbnails',

    # rest framework
    'rest_framework',

    # filters
    'django_filters',

    # swagger
    'drf_yasg',
    'rest_framework_swagger',

    # site apps
    'matcha',
    'chat',

    # chat
    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'dating_site.middlewares.CustomMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'dating_site.urls'

####################################
# Templates
####################################

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dating_site.context_processors.global_user',
            ],
        },
    },
]

WSGI_APPLICATION = 'dating_site.wsgi.application'

####################################
# Databases
####################################

import pymysql

pymysql.install_as_MySQLdb()

DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': 3306
    }
}

# see https://github.com/maxtepkeev/architect/issues/38
CONN_MAX_AGE = None

####################################
# REST
####################################

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'EXCEPTION_HANDLER': 'matcha.utils.custom_exception_handler'
}

####################################
# Password validation
####################################

AUTH_USER_MODEL = "matcha.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

####################################
# Static files (CSS, JavaScript, Images)
####################################

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_PREFIX = 'media/images'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

####################################
# Registration
####################################

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True
REGISTRATION_USE_SITE_EMAIL = True
SITE_ID = 1
REGISTRATION_FORM = 'matcha.forms.CustomRegistrationForm'

####################################
# Chat
####################################

ASGI_APPLICATION = 'dating_site.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

####################################
# Debug
####################################

INTERNAL_IPS = [
    '127.0.0.1',
]

####################################
# VERBOSE
####################################

verbose_flag = False

####################################
# REDIS
####################################

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_BASE_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
# NB: for django-health-check
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'

####################################
# CELERY
####################################

CELERY_REDIS_DB = os.getenv('CELERY_REDIS_DB', '0')
CELERY_BROKER_URL = f'{REDIS_BASE_URL}/{CELERY_REDIS_DB}'
CELERY_RESULT_BACKEND = f'{REDIS_BASE_URL}/{CELERY_REDIS_DB}'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': CELERY_BROKER_URL,
        'default_timeout': 60 * 60
    }
}

####################################
# Custom Pagination
####################################

PAGE_SIZE = 5

####################################
# Search settings
####################################

MAX_RATING = 9999
MAX_AGE = 110

####################################
# Local Settings
####################################

from .local_settings import *
