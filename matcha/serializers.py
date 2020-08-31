from rest_framework import serializers

from .models import (
    Tag, User, UserTag, UserPhoto, UsersConnect
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag

    def to_representation(self, instance):
        return TagReadSerializer(instance).data


class TagReadSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


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


class UsersConnectSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = UsersConnect

    def to_representation(self, instance):
        return UsersConnectReadSerializer(instance).data


class UsersConnectReadSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = UsersConnect

    user_1 = serializers.SerializerMethodField()
    user_2 = serializers.SerializerMethodField()

    @staticmethod
    def get_user_1(instance: UsersConnect):
        return UserReadSerializer(instance.user_1).data

    @staticmethod
    def get_user_2(instance: UsersConnect):
        return UserReadSerializer(instance.user_2).data
