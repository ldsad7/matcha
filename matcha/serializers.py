from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, ErrorDetail
from rest_framework.fields import (
    CharField, IntegerField, DateTimeField
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

    def get_field(self, field):
        return self.model._declared_fields[field]

    def get_model_field_attr(self, model_field, attr):
        return getattr(model_field, attr, None)

    def run_validation(self, data=None):
        if not data:
            raise_exception('Запрос', 'Некорректный запрос')
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

            if isinstance(getattr(self.main_model, field), ForwardManyToOneDescriptor):
                pass
            if isinstance(getattr(self.main_model, field.strip('_id')), ForwardManyToOneDescriptor):
                pass
            model_field = self.get_field(field)
            required = self.get_model_field_attr(model_field, 'required')
            read_only = self.get_model_field_attr(model_field, 'read_only')
            if field in data:
                value = data[field]
                if field in unique_together:
                    unique_together_dict[field] = value
                if read_only:
                    raise_exception(field, 'Это поле read_only')
                allow_null = self.get_model_field_attr(model_field, 'allow_null')
                if not allow_null and value is None:
                    raise_exception(field, 'Это поле не может быть нулевым')
                if isinstance(model_field, CharField):
                    if not isinstance(value, str):
                        raise_exception(field, 'Значение не соответствует типу поля')
                    allow_blank = self.get_model_field_attr(model_field, 'allow_blank')
                    if not allow_blank and not value:
                        raise_exception(field, 'Это поле не может быть пустым')
                    max_length = self.get_model_field_attr(model_field, 'max_length')
                    if max_length is not None and len(value) > max_length:
                        raise_exception(field, f'Это поле не может быть длиной более {max_length}')
                    min_length = self.get_model_field_attr(model_field, 'min_length')
                    if min_length is not None and len(value) < min_length:
                        raise_exception(field, f'Это поле не может быть длиной менее {min_length}')
                elif isinstance(model_field, DateTimeField):
                    if not isinstance(value, str):
                        raise_exception(field, 'Значение не соответствует типу поля')
                elif isinstance(model_field, IntegerField):
                    if not isinstance(value, int):
                        raise_exception(field, 'Значение не соответствует типу поля')
            elif required:
                raise_exception(field, 'Это поле должно обязательно присутствовать в запросе')
        if self.main_model.objects_.filter(**unique_together_dict):
            raise_exception(', '.join(unique_together_dict), 'Эти поля должны образовывать уникальный набор')
        # print(f'data: {data}')
        return data

    def create(self, validated_data):
        c = self.model()
        for field in self.model_fields_without_id:
            setattr(c, field, validated_data.get(field))
        c.save()
        return c

    def update(self, c, validated_data):
        for field in self.model_fields:
            setattr(c, field, validated_data.get(field, getattr(c, field)))
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = User

    def to_representation(self, instance):
        return UserReadSerializer(instance).data


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'last_login', 'username', 'first_name', 'last_name', 'email', 'is_active',
            'gender', 'orientation', 'date_of_birth', 'info', 'location', 'tags', 'photos',
            'profile_activated'
        )
        model = User

    tags = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()

    @staticmethod
    def get_tags(instance: User):
        return UserTagReadSerializer(UserTag.objects.filter(user=instance), many=True).data

    @staticmethod
    def get_photos(instance: User):
        return UserPhotoReadSerializer(UserPhoto.objects.filter(user=instance), many=True).data


class UserTagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = UserTag

    def to_representation(self, instance):
        return UserTagReadSerializer(instance).data


class UserTagReadSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = UserTag

    user = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()

    @staticmethod
    def get_user(instance: UserTag):
        return instance.user.username

    @staticmethod
    def get_tag(instance: UserTag):
        return instance.tag.name


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = UserPhoto

    def to_representation(self, instance):
        return UserPhotoReadSerializer(instance).data


class UserPhotoReadSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = UserPhoto


# class UsersConnectSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = '__all__'
#         model = UsersConnect
#
#     def to_representation(self, instance):
#         return UsersConnectReadSerializer(instance).data
#
#
# class UsersConnectReadSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = '__all__'
#         model = UsersConnect
#
    # user_1 = serializers.SerializerMethodField()
    # user_2 = serializers.SerializerMethodField()
    #
    # @staticmethod
    # def get_user_1(instance: UsersConnect):
    #     return UserReadSerializer(instance.user_1).data
    #
    # @staticmethod
    # def get_user_2(instance: UsersConnect):
    #     return UserReadSerializer(instance.user_2).data


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
