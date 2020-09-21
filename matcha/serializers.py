import string
from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, ErrorDetail
from rest_framework.fields import (
    CharField, IntegerField, DateTimeField, FloatField, BooleanField,
    ImageField, empty
)

from .models import (
    Tag, User, UserTag, UserPhoto, UsersConnect
)


def raise_exception(field, text):
    raise ValidationError(detail={
        field: [
            ErrorDetail(
                string=text
            )
        ]
    })


def str_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError


class CommonSerializer(serializers.Serializer):
    @property
    def model(self):
        return CommonSerializer

    @property
    def main_model(self):
        return CommonSerializer

    @property
    def model_fields(self):
        return list(self.model._declared_fields.keys())

    @property
    def model_fields_without_id(self):
        return [field for field in self.model_fields if field != 'id']

    @property
    def unique_fields(self):
        return []

    def get_field(self, field):
        return self.model._declared_fields[field]

    def get_model_field_attr(self, model_field, attr):
        return getattr(model_field, attr, None)

    def run_validation(self, data=None):
        if not data:
            raise_exception('Запрос', 'Некорректный запрос')
        new_data = {}
        for key, value in data.items():
            new_data[key] = value
        data = new_data
        model_fields = self.model_fields
        # print(f'model_fields: {model_fields}')
        diff = set(data) - set(model_fields)
        if diff:
            raise_exception(diff.pop(), 'Неизвестное поле')
        unique_together = self.main_model._meta.unique_together
        if unique_together:
            unique_together = list(unique_together[0])
        # print(f'unique_together: {unique_together}')
        for i, field in enumerate(unique_together):
            if isinstance(getattr(self.main_model, field), ForwardManyToOneDescriptor):
                unique_together[i] += '_id'
        unique_together_dict = {}
        for field in model_fields:
            model_field = self.get_field(field)
            required = self.get_model_field_attr(model_field, 'required')
            read_only = self.get_model_field_attr(model_field, 'read_only')
            allow_null = self.get_model_field_attr(model_field, 'allow_null')
            allow_blank = self.get_model_field_attr(model_field, 'allow_blank')
            if field in data:
                value = data[field]
                if field == 'username':
                    diff = set(value) - set(string.digits + string.ascii_letters + '@.+-_')
                    if diff:
                        raise_exception(field, f'Это поле содержит недопустимые символы: {", ".join(diff)}')
                if field in unique_together:
                    unique_together_dict[field] = value
                if read_only:
                    raise_exception(field, 'Это поле read_only')
                if not allow_null and value is None:
                    raise_exception(field, 'Это поле не может быть нулевым')
                if isinstance(model_field, CharField):
                    if not isinstance(value, str):
                        raise_exception(field, 'Значение не соответствует типу поля')
                    if not allow_blank and not value:
                        raise_exception(field, 'Это поле не может быть пустым')
                    max_length = self.get_model_field_attr(model_field, 'max_length')
                    if max_length is not None and len(value) > max_length:
                        raise_exception(field, f'Это поле не может быть длиной более {max_length}')
                    min_length = self.get_model_field_attr(model_field, 'min_length')
                    if min_length is not None and len(value) < min_length:
                        raise_exception(field, f'Это поле не может быть длиной менее {min_length}')
                    if allow_blank:
                        data[field] = value
                elif isinstance(model_field, DateTimeField):
                    if not isinstance(value, str):
                        raise_exception(field, 'Значение не соответствует типу поля')
                elif isinstance(model_field, IntegerField):
                    if not isinstance(value, int):
                        try:
                            data[field] = int(value)
                        except ValueError:
                            raise_exception(field, 'Значение не соответствует типу поля')
                elif isinstance(model_field, FloatField):
                    if not isinstance(value, float):
                        try:
                            data[field] = float(value)
                        except ValueError:
                            raise_exception(field, 'Значение не соответствует типу поля')
                elif isinstance(model_field, ImageField):
                    pass
                elif isinstance(model_field, BooleanField):
                    if not isinstance(value, bool):
                        try:
                            data[field] = int(str_to_bool(value))
                        except ValueError:
                            raise_exception(field, 'Значение не соответствует типу поля')

                obj = getattr(self.main_model, field.strip('_id'), None)
                if isinstance(obj, ForwardManyToOneDescriptor):
                    if not obj.field.remote_field.model.objects.filter(id=value):
                        raise_exception(field, 'Не существует такого значения в базе')
                if allow_null and not value:
                    data[field] = None
            elif required:
                raise_exception(field, 'Это поле должно обязательно присутствовать в запросе')
            else:
                if allow_null:
                    data[field] = None
                if allow_blank:
                    data[field] = ''
                default = self.get_model_field_attr(model_field, 'default')
                if default is not None and default != empty:
                    data[field] = default

        # print(f'unique_together_dict: {unique_together_dict}, unique_together: {unique_together}')
        if self.main_model.objects_.filter(**unique_together_dict):
            raise_exception(', '.join(unique_together_dict), 'Эти поля должны образовывать уникальный набор')
        for field in self.unique_fields:
            if field in data and self.main_model.objects_.filter(**{field: data[field]}):
                raise_exception(field, 'Это поле должно быть уникальным')
        # print(f'data: {data}')
        return data

    def create(self, validated_data):
        c = self.main_model()
        for field in self.model_fields_without_id:
            setattr(c, field, validated_data.get(field))
        c.save()
        return c

    def update(self, c, validated_data):
        for field in self.model_fields:
            setattr(c, field, validated_data.get(field, getattr(c, field, None)))
        c.save()
        return c

    def is_valid(self, raise_exception=False):
        if not hasattr(self, '_validated_data'):
            try:
                self._validated_data = self.run_validation(self.initial_data)
            except ValidationError as exc:
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}
        if self._errors and raise_exception:
            raise ValidationError(self.errors)
        return not bool(self._errors)

    def save(self, **kwargs):
        validated_data = dict(
            list(self.validated_data.items()) + list(kwargs.items())
        )
        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data)
            assert self.instance is not None, (
                '`update()` did not return an object instance.'
            )
        else:
            self.instance = self.create(validated_data)
            assert self.instance is not None, (
                '`create()` did not return an object instance.'
            )
        return self.instance

    @property
    def validated_data(self):
        return self._validated_data

    class Meta:
        validators = []


class TagSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=False, allow_blank=False, max_length=32)
    created = serializers.DateTimeField(required=False)
    modified = serializers.DateTimeField(required=False)

    @property
    def model(self):
        return TagSerializer

    @property
    def main_model(self):
        return Tag

    # class Meta(CommonSerializer.Meta):
    #     pass


class UserSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(required=False, max_length=128)
    last_login = serializers.DateTimeField(required=False, allow_null=True)
    username = serializers.CharField(required=False, max_length=150)
    is_superuser = serializers.BooleanField(required=False, default=False)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150, default='')
    email = serializers.EmailField(required=False)
    is_staff = serializers.BooleanField(required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)
    date_joined = serializers.DateTimeField(required=False)
    gender = serializers.CharField(required=False, max_length=32, default=User.UNKNOWN)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    info = serializers.CharField(required=False, allow_blank=True, max_length=4096, default='')
    location = serializers.CharField(required=False, allow_blank=True, max_length=512, default='')
    profile_activated = serializers.BooleanField(required=False, default=False)
    orientation = serializers.CharField(required=False, max_length=32, default=User.UNKNOWN)
    latitude = serializers.FloatField(required=False, default=0.0)
    longitude = serializers.FloatField(required=False, default=0.0)
    tags = serializers.ListField(required=False, default=[])
    photos = serializers.ListField(required=False, default=[])

    @property
    def unique_fields(self):
        return ['username', 'email']

    @property
    def model(self):
        return UserSerializer

    @property
    def main_model(self):
        return User


class UserReadSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    last_login = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False, allow_null=True)
    username = serializers.CharField(required=False, max_length=150)
    is_superuser = serializers.BooleanField(required=False, default=False)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150, default='')
    email = serializers.EmailField(required=True)
    is_staff = serializers.BooleanField(required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)
    date_joined = serializers.DateTimeField(required=False)
    gender = serializers.CharField(required=False, max_length=32, default=User.UNKNOWN)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    info = serializers.CharField(required=False, allow_blank=True, max_length=4096, default='')
    location = serializers.CharField(required=False, allow_blank=True, max_length=512, default='')
    profile_activated = serializers.BooleanField(required=False, default=False)
    orientation = serializers.CharField(required=False, max_length=32, default=User.UNKNOWN)
    latitude = serializers.FloatField(required=False, default=0.0)
    longitude = serializers.FloatField(required=False, default=0.0)
    rating = serializers.FloatField(required=False, default=0.0)
    tags = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()

    @staticmethod
    def get_last_login(instance: User):
        if instance.last_login:
            if datetime.now().replace(tzinfo=pytz.UTC) - timedelta(minutes=5) < instance.last_login.replace(tzinfo=pytz.UTC):
                return 'online'
            else:
                return instance.last_login
        return 'offline'

    @staticmethod
    def get_tags(instance: User):
        return UserTagReadSerializer(UserTag.objects_.filter(user_id=instance.id), many=True).data

    @staticmethod
    def get_photos(instance: User):
        return UserPhotoReadSerializer(UserPhoto.objects_.filter(user_id=instance.id), many=True).data

    @property
    def model(self):
        return UserReadSerializer

    @property
    def main_model(self):
        return User


class UserTagSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(required=True)
    tag_id = serializers.IntegerField(required=True)
    created = serializers.DateTimeField(required=False)
    modified = serializers.DateTimeField(required=False)

    @property
    def model(self):
        return UserTagSerializer

    @property
    def main_model(self):
        return UserTag


class UserTagReadSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()
    created = serializers.DateTimeField(required=False)
    modified = serializers.DateTimeField(required=False)

    @staticmethod
    def get_user(instance: UserTag):
        return instance.user.username

    @staticmethod
    def get_tag(instance: UserTag):
        return instance.tag.name

    @property
    def model(self):
        return UserTagReadSerializer

    @property
    def main_model(self):
        return UserTag


class UserPhotoSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=32)
    image = serializers.ImageField(required=False)
    main = serializers.BooleanField(required=False, default=False)
    user_id = serializers.IntegerField(required=True)
    created = serializers.DateTimeField(required=False)
    modified = serializers.DateTimeField(required=False)

    @property
    def model(self):
        return UserPhotoSerializer

    @property
    def main_model(self):
        return UserPhoto


class UserPhotoReadSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=32)
    image = serializers.SerializerMethodField()
    main = serializers.BooleanField(required=False, default=False)
    user = serializers.SerializerMethodField()
    created = serializers.DateTimeField(required=False)
    modified = serializers.DateTimeField(required=False)

    @staticmethod
    def get_user(instance: UserPhoto):
        return instance.user.id

    # @staticmethod
    def get_image(self, instance: UserPhoto):
        return f'{settings.MEDIA_URL}{self.main_model.image.field.upload_to}{instance.image}'

    @property
    def model(self):
        return UserPhotoReadSerializer

    @property
    def main_model(self):
        return UserPhoto


class UsersConnectSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    user_1_id = serializers.IntegerField(required=True)
    user_2_id = serializers.IntegerField(required=True)
    created = serializers.DateTimeField(required=False)
    modified = serializers.DateTimeField(required=False)

    @property
    def model(self):
        return UsersConnectSerializer

    @property
    def main_model(self):
        return UsersConnect


class UsersConnectReadSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    user_1 = serializers.SerializerMethodField()
    user_2 = serializers.SerializerMethodField()
    created = serializers.DateTimeField(required=False)
    modified = serializers.DateTimeField(required=False)

    @staticmethod
    def get_user_1(instance: UsersConnect):
        return UserReadSerializer(instance.user_1).data

    @staticmethod
    def get_user_2(instance: UsersConnect):
        return UserReadSerializer(instance.user_2).data

    @property
    def model(self):
        return UsersConnectReadSerializer

    @property
    def main_model(self):
        return UsersConnect
