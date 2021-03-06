import string
from datetime import datetime, timedelta, date

import pytz
from django.conf import settings
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.fields import (
    CharField, IntegerField, DateTimeField, FloatField, BooleanField,
    ImageField, empty
)

from dating_site.settings import MEDIA_PREFIX

from .models import (
    Tag, User, UserTag, UserPhoto, UsersConnect, UsersFake, UsersBlackList, Notification, Message,
    UsersRating)


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

    @staticmethod
    def get_modified(instance):
        return instance.modified.replace(tzinfo=pytz.UTC).astimezone(timezone.get_current_timezone())

    @staticmethod
    def get_created(instance):
        return instance.created.replace(tzinfo=pytz.UTC).astimezone(timezone.get_current_timezone())

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
                    diff = set(value) - set(string.digits + string.ascii_letters + '@.+-')
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
            if field in data:
                objs = self.main_model.objects_.filter(**{field: data[field]})
                objs = [obj for obj in objs if int(obj.id) != self.context['user_id']]
                if objs:
                    raise_exception(field, 'Это поле должно быть уникальным')
        # print(f'data: {data}')
        return data

    def create(self, validated_data):
        c = self.main_model()
        for field in self.model_fields_without_id:
            setattr(c, field, validated_data.get(field))
            print(f'field: {field}, validated_data.get(field): {validated_data.get(field)}')
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
    # password = serializers.CharField(required=False, max_length=128)
    # last_login = serializers.DateTimeField(required=False, allow_null=True, read_only=True)
    # last_online = serializers.DateTimeField(required=False, allow_null=True, read_only=True)
    # username = serializers.CharField(required=False, max_length=150)
    # is_superuser = serializers.BooleanField(required=False, default=False)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150, default='')
    email = serializers.EmailField(required=False, allow_blank=True, max_length=254, default='')
    # is_staff = serializers.BooleanField(required=False, default=False)
    # is_active = serializers.BooleanField(required=False, default=True)
    # date_joined = serializers.DateTimeField(required=False)
    gender = serializers.CharField(required=False, max_length=32, default=User.UNKNOWN)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    info = serializers.CharField(required=False, allow_blank=True, max_length=4096, default='')
    location = serializers.CharField(required=False, allow_blank=True, max_length=512, default='')
    # profile_activated = serializers.BooleanField(required=False, default=False)
    orientation = serializers.CharField(required=False, max_length=32, default=User.UNKNOWN)
    # latitude = serializers.FloatField(required=False, default=0.0)
    # longitude = serializers.FloatField(required=False, default=0.0)
    # country = serializers.CharField(required=False, max_length=64, allow_blank=False, allow_null=True)
    # city = serializers.CharField(required=False, max_length=64, allow_blank=False, allow_null=True)
    # rating = serializers.FloatField(required=False, default=0.0)
    tags = serializers.ListField(required=False, default=[])
    # photos = serializers.ListField(required=False, default=[])
    # main_photo = serializers.CharField(required=False, max_length=128, allow_blank=False, allow_null=True)

    # tags = serializers.SerializerMethodField()
    # photos = serializers.SerializerMethodField()
    # last_login = serializers.SerializerMethodField()

    # @staticmethod
    # def get_last_online(instance: User):
    #     if instance.last_online:
    #         if datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(minutes=5) < \
    #                 instance.last_online.replace(tzinfo=pytz.UTC):
    #             return 'online'
    #         else:
    #             return instance.last_online.replace(tzinfo=pytz.UTC)
    #     return 'offline'

    # @staticmethod
    # def get_tags(instance: User):
    #     user_tags = UserTag.objects_.filter(user_id=instance.id)
    #     tags = [user_tag.tag.name for user_tag in user_tags]
    #     return tags

    # @staticmethod
    # def get_photos(instance: User):
    #     user_photos = UserPhoto.objects_.filter(user_id=instance.id)
    #     photos = [f'/{MEDIA_PREFIX}/{user_photo.image}' for user_photo in user_photos]
    #     return photos

    @property
    def unique_fields(self):
        return ['username', 'email']

    @property
    def model(self):
        return UserSerializer

    @property
    def main_model(self):
        return User


class ShortUserSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    # last_login = serializers.DateTimeField(required=False, allow_null=True)
    username = serializers.CharField(required=False, max_length=150)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150, default='')
    info = serializers.CharField(required=False, allow_blank=True, max_length=4096, default='')
    orientation = serializers.CharField(required=False, max_length=32, default=User.UNKNOWN)
    rating = serializers.FloatField(required=False, default=0.0)
    email = serializers.EmailField(required=False, allow_blank=True, max_length=254, default='')
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True, max_length=512, default='')
    latitude = serializers.FloatField(required=False, default=0.0)
    longitude = serializers.FloatField(required=False, default=0.0)

    last_online = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    main_photo = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    @staticmethod
    def get_last_online(instance: User):
        if instance.last_online:
            if datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(minutes=5) < \
                    instance.last_online.replace(tzinfo=pytz.UTC):
                return 'online'
            else:
                return instance.last_online.replace(tzinfo=pytz.UTC)
        return 'offline'

    @staticmethod
    def get_age(instance: User):
        today = date.today()
        born = instance.date_of_birth
        try:
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        except AttributeError:
            return 'неизвестно, сколько'

    @staticmethod
    def get_tags(instance: User):
        user_tags = UserTag.objects_.filter(user_id=instance.id)
        tags = [user_tag.tag.name for user_tag in user_tags]
        return tags

    @staticmethod
    def get_photos(instance: User):
        user_photos = UserPhoto.objects_.filter(user_id=instance.id)
        photos = [f'/{MEDIA_PREFIX}/{user_photo.image}' for user_photo in user_photos if not user_photo.main]
        return photos

    @staticmethod
    def get_main_photo(instance: User):
        user_photos = UserPhoto.objects_.filter(user_id=instance.id)
        photos = [f'/{MEDIA_PREFIX}/{user_photo.image}' for user_photo in user_photos if user_photo.main]
        if photos:
            return photos[0]

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
    username = serializers.CharField(required=False, max_length=150)
    # is_superuser = serializers.BooleanField(required=False, default=False)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150, default='')
    email = serializers.EmailField(required=False, allow_blank=True, max_length=254, default='')
    # is_staff = serializers.BooleanField(required=False, default=False)
    # is_active = serializers.BooleanField(required=False, default=True)
    gender = serializers.CharField(required=False, max_length=32, default=User.UNKNOWN)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    info = serializers.CharField(required=False, allow_blank=True, max_length=4096, default='')
    location = serializers.CharField(required=False, allow_blank=True, max_length=512, default='')
    profile_activated = serializers.BooleanField(required=False, default=False)
    orientation = serializers.CharField(required=False, max_length=32, default=User.UNKNOWN)
    latitude = serializers.FloatField(required=False, default=0.0)
    longitude = serializers.FloatField(required=False, default=0.0)
    country = serializers.CharField(required=False, max_length=64, allow_blank=False, allow_null=True)
    city = serializers.CharField(required=False, max_length=64, allow_blank=False, allow_null=True)
    rating = serializers.FloatField(required=False, default=0.0)

    # date_joined = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)
    last_online = serializers.SerializerMethodField()
    # fake_accusations = serializers.SerializerMethodField()  # serializers.IntegerField(required=False, default=0)
    tags = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    main_photo = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    # @staticmethod
    # def get_date_joined(instance: User):
    #     return instance.date_joined.replace(tzinfo=pytz.UTC)

    @staticmethod
    def get_age(instance: User):
        today = date.today()
        born = instance.date_of_birth
        try:
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        except AttributeError:
            return 'неизвестно, сколько'

    @staticmethod
    def get_last_online(instance: User):
        if instance.last_online:
            if datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(minutes=5) < \
                    instance.last_online.replace(tzinfo=pytz.UTC):
                return 'online'
            else:
                return instance.last_online.replace(tzinfo=pytz.UTC)
        return 'offline'

    # @staticmethod
    # def get_fake_accusations(instance: User):
    #     return len(UsersFake.objects_.filter(user_2_id=instance.id))

    # @staticmethod
    # def get_tags(instance: User):
    #     return UserTagReadSerializer(UserTag.objects_.filter(user_id=instance.id), many=True).data
    #
    # @staticmethod
    # def get_photos(instance: User):
    #     return UserPhotoReadSerializer(UserPhoto.objects_.filter(user_id=instance.id), many=True).data

    @staticmethod
    def get_tags(instance: User):
        user_tags = UserTag.objects_.filter(user_id=instance.id)
        tags = [user_tag.tag.name for user_tag in user_tags]
        return tags

    @staticmethod
    def get_photos(instance: User):
        user_photos = UserPhoto.objects_.filter(user_id=instance.id)
        photos = [f'/{MEDIA_PREFIX}/{user_photo.image}' for user_photo in user_photos if not user_photo.main]
        return photos

    @staticmethod
    def get_main_photo(instance: User):
        user_photos = UserPhoto.objects_.filter(user_id=instance.id)
        photos = [f'/{MEDIA_PREFIX}/{user_photo.image}' for user_photo in user_photos if user_photo.main]
        if photos:
            return photos[0]

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
    created = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)
    modified = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)

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
    image = serializers.CharField(required=False)  # ImageField
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
    created = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)
    modified = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)

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
    user_1_id = serializers.IntegerField(required=False)
    user_2_id = serializers.IntegerField(required=False)
    type = serializers.CharField(required=False, max_length=32)
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
    type = serializers.CharField(required=True, max_length=32)
    created = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)
    modified = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)

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


class UsersFakeSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    user_1_id = serializers.IntegerField(required=True)
    user_2_id = serializers.IntegerField(required=True)
    created = serializers.DateTimeField(required=False)
    modified = serializers.DateTimeField(required=False)

    @property
    def model(self):
        return UsersFakeSerializer

    @property
    def main_model(self):
        return UsersFake


class UsersFakeReadSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    user_1 = serializers.SerializerMethodField()
    user_2 = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)
    modified = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)

    @staticmethod
    def get_user_1(instance: UsersFake):
        return UserReadSerializer(instance.user_1).data

    @staticmethod
    def get_user_2(instance: UsersFake):
        return UserReadSerializer(instance.user_2).data

    @property
    def model(self):
        return UsersFakeReadSerializer

    @property
    def main_model(self):
        return UsersFake


class UsersBlackListSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    user_1_id = serializers.IntegerField(required=True)
    user_2_id = serializers.IntegerField(required=True)
    created = serializers.DateTimeField(required=False)
    modified = serializers.DateTimeField(required=False)

    @property
    def model(self):
        return UsersBlackListSerializer

    @property
    def main_model(self):
        return UsersBlackList


class UsersBlackListReadSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    user_1 = serializers.SerializerMethodField()
    user_2 = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)
    modified = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)

    @staticmethod
    def get_user_1(instance: UsersBlackList):
        return UserReadSerializer(instance.user_1).data

    @staticmethod
    def get_user_2(instance: UsersBlackList):
        return UserReadSerializer(instance.user_2).data

    @property
    def model(self):
        return UsersBlackListReadSerializer

    @property
    def main_model(self):
        return UsersBlackList


class UsersRatingSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    user_1_id = serializers.IntegerField(required=True)
    user_2_id = serializers.IntegerField(required=True)
    rating = serializers.FloatField(required=True)
    created = serializers.DateTimeField(required=False)
    modified = serializers.DateTimeField(required=False)

    @property
    def model(self):
        return UsersRatingSerializer

    @property
    def main_model(self):
        return UsersRating


class UsersRatingReadSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    user_1 = serializers.SerializerMethodField()
    user_2 = serializers.SerializerMethodField()
    rating = serializers.FloatField(required=True)
    created = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)
    modified = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)

    @staticmethod
    def get_user_1(instance: UsersRating):
        return UserReadSerializer(instance.user_1).data

    @staticmethod
    def get_user_2(instance: UsersRating):
        return UserReadSerializer(instance.user_2).data

    @property
    def model(self):
        return UsersRatingReadSerializer

    @property
    def main_model(self):
        return UsersRating


class NotificationSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(required=True, max_length=32)
    user_1_id = serializers.IntegerField(required=True)
    user_2_id = serializers.IntegerField(required=True)
    was_read = serializers.BooleanField(required=False, default=False)
    created = serializers.DateTimeField(required=False)
    modified = serializers.DateTimeField(required=False)

    @property
    def model(self):
        return NotificationSerializer

    @property
    def main_model(self):
        return Notification


class ShortNotificationReadSerializer(CommonSerializer):
    # id = serializers.IntegerField(read_only=True)
    # type = serializers.CharField(required=True, max_length=32)
    # user_1 = serializers.SerializerMethodField()
    # user_2 = serializers.SerializerMethodField()
    # was_read = serializers.BooleanField(required=False, default=False)
    created = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)
    # modified = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)

    message = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    @staticmethod
    def get_user_id(instance: Notification):
        if instance.to:
            return instance.user_1_id
        return instance.user_2_id

    @staticmethod
    def get_message(instance: Notification):
        if instance.to:
            user_id = instance.user_1_id
        else:
            user_id = instance.user_2_id
        user = User.objects_.get(id=user_id)
        message = ''
        if instance.type == Notification.LIKE:
            if instance.to:
                message = 'Вас лайкнул(а) '
            else:
                message = 'Вы поставили лайк '
        elif instance.type == Notification.PROFILE:
            if instance.to:
                message = 'Ваш профиль был просмотрен '
            else:
                message = 'Вы просмотрели профиль '
        elif instance.type == Notification.MESSAGE:
            if instance.to:
                message = 'Вам было отправлено сообщение от '
            else:
                message = 'Вы отправили сообщение '
        elif instance.type == Notification.LIKE_BACK:
            if instance.to:
                message = 'Вас лайкнул(а) в ответ '
            else:
                message = 'Вы лайкнули в ответ '
        elif instance.type == Notification.IGNORE:
            if instance.to:
                message = 'Вас проигнорировал(а) в ответ '
            else:
                message = 'Вы проигнорировали в ответ '
        message += f'{user.first_name} {user.last_name} ({user.username})'
        return message

    @staticmethod
    def get_image(instance: Notification):
        if instance.to:
            user_id = instance.user_1_id
        else:
            user_id = instance.user_2_id
        photos = UserPhoto.objects_.filter(user_id=user_id)
        main_photos = [photo for photo in photos if photo.main]
        if main_photos:
            return f'/{MEDIA_PREFIX}/{main_photos[0].image}'
        elif photos:
            return f'/{MEDIA_PREFIX}/{photos[0].image}'

    @staticmethod
    def get_created(instance: Notification):
        return instance.created.replace(tzinfo=pytz.UTC)

    # @staticmethod
    # def get_modified(instance: Notification):
    #     return instance.modified.replace(tzinfo=pytz.UTC)

    @staticmethod
    def get_user_1(instance: Notification):
        return instance.user_1.id

    @staticmethod
    def get_user_2(instance: Notification):
        return instance.user_2.id

    @property
    def model(self):
        return NotificationReadSerializer

    @property
    def main_model(self):
        return Notification


class NotificationReadSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(required=True, max_length=32)
    user_1 = serializers.SerializerMethodField()
    user_2 = serializers.SerializerMethodField()
    was_read = serializers.BooleanField(required=False, default=False)
    created = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)
    modified = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)

    @staticmethod
    def get_created(instance: Notification):
        return instance.created.replace(tzinfo=pytz.UTC)

    @staticmethod
    def get_modified(instance: Notification):
        return instance.modified.replace(tzinfo=pytz.UTC)

    @staticmethod
    def get_user_1(instance: Notification):
        return instance.user_1.id

    @staticmethod
    def get_user_2(instance: Notification):
        return instance.user_2.id

    @property
    def model(self):
        return NotificationReadSerializer

    @property
    def main_model(self):
        return Notification


class MessageSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(required=True, max_length=32)
    user_1_id = serializers.IntegerField(required=True)
    user_2_id = serializers.IntegerField(required=True)
    message = serializers.CharField(required=True, max_length=256)
    created = serializers.DateTimeField(required=False)
    modified = serializers.DateTimeField(required=False)

    @property
    def model(self):
        return MessageSerializer

    @property
    def main_model(self):
        return Message


class MessageReadSerializer(CommonSerializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(required=True, max_length=32)
    user_1 = serializers.SerializerMethodField()
    user_2 = serializers.SerializerMethodField()
    message = serializers.CharField(required=True, max_length=256)
    created = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)
    modified = serializers.SerializerMethodField()  # serializers.DateTimeField(required=False)

    @staticmethod
    def get_created(instance: Message):
        return instance.created.replace(tzinfo=pytz.UTC)

    @staticmethod
    def get_modified(instance: Message):
        return instance.modified.replace(tzinfo=pytz.UTC)

    @staticmethod
    def get_user_1(instance: Message):
        return {
            'id': instance.user_1.id,
            'username': instance.user_1.username
        }

    @staticmethod
    def get_user_2(instance: Message):
        return {
            'id': instance.user_2.id,
            'username': instance.user_2.username
        }

    @property
    def model(self):
        return MessageReadSerializer

    @property
    def main_model(self):
        return Message
