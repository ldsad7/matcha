from django.contrib import admin

from .models import (
    Tag, User, UserTag, UserPhoto
)

for class_ in [Tag, User, UserTag, UserPhoto]:
    admin.site.register(class_)
