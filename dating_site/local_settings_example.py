SECRET_KEY = '<...>'
DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'NAME',
        'USER': 'USER',
        'PASSWORD': 'PASSWORD',
        'HOST': '127.0.0.1',
        'PORT': 3306
    }
}

####################################
# MAIL
####################################

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_USER = "tmp@yandex.ru"
EMAIL_HOST_PASSWORD = "EMAIL_HOST_PASSWORD"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
REGISTRATION_SITE_USER_EMAIL = 'tmp'

####################################
# Yandex Maps
####################################

API_KEY = 'API_KEY'
