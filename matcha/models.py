from datetime import datetime, date

from django.db import models
from django.utils.functional import cached_property
from model_utils.models import TimeStampedModel
from django.contrib.auth.models import AbstractUser
from model_utils import Choices
from django.utils.translation import ugettext_lazy as _
from .common import get_by_model_and_id, get_thumb
from .managers import (
    TagManager, UsersConnectManager, UserTagManager, UserPhotoManager, UserManager,
    UsersFakeManager, UsersBlackListManager, NotificationManager, MessageManager,
    UsersRatingManager)


class ManagedModel:
    def save(self, **kwargs):
        if self.id is not None:
            return self.objects_.update(self)
        else:
            return self.objects_.insert(self)

    def delete(self, **kwargs):
        self.objects_.delete(self)


class GetById:
    def get_by_id(self, _id):
        return get_by_model_and_id(self, _id)


class Tag(ManagedModel, TimeStampedModel, GetById):
    name = models.CharField(_('название'), max_length=32, blank=False, null=False)
    objects_ = TagManager()

    def __str__(self):
        return f"Tag {self.name}"

    class Meta:
        db_table = 'matcha_tag'
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        unique_together = ('name',)


class User(ManagedModel, AbstractUser, GetById):
    UNKNOWN = "неизвестно"

    MAN = "мужской"
    WOMAN = "женский"
    GENDERS = Choices(
        (MAN, "man"), (WOMAN, "woman"), (UNKNOWN, "unknown")
    )

    HETERO = "гетеросексуальность"
    HOMO = "гомосексуальность"
    BI = "бисекусальность"
    ORIENTATIONS = Choices(
        (HETERO, "heterosexual"), (HOMO, "homosexual"), (BI, "bisexual"),
        (UNKNOWN, "unknown")
    )

    email = models.EmailField(_('email address'), blank=False, null=False, unique=True)
    gender = models.CharField(_('пол'), max_length=32, choices=GENDERS, default=UNKNOWN)
    orientation = models.CharField(_('ориентация'), max_length=32, choices=ORIENTATIONS, default=UNKNOWN)
    date_of_birth = models.DateField(_('дата рождения'), blank=False, null=True)
    info = models.CharField(_('краткое описание'), max_length=4096, blank=True, null=False)
    location = models.CharField(_('местоположение'), max_length=512, blank=True, null=False)
    profile_activated = models.BooleanField(_('профиль активирован'), blank=False, null=False, default=False)
    latitude = models.FloatField(_('широта'), default=0.0)
    longitude = models.FloatField(_('долгота'), default=0.0)
    country = models.CharField(_('страна'), max_length=64, blank=False, null=True)
    city = models.CharField(_('город'), max_length=64, blank=False, null=True)
    rating = models.FloatField(_('рейтинг'), default=0.0)
    objects_ = UserManager()

    @property
    def age(self):
        bday = datetime.strptime(self.date_of_birth, '%Y-%m-%d')
        d = date.today()
        return (d.year - bday.year) - int((d.month, d.day) < (bday.month, bday.day))

    def save(self, *args, **kwargs):
        was_empty_field = False
        for field in self._meta.fields:
            name = field.name
            value = getattr(self, field.name)
            if (name in ['first_name', 'last_name', 'info', 'location', 'date_of_birth'] and not value) or \
                    (name in ['gender', 'orientation'] and value == self.UNKNOWN):
                was_empty_field = True
                break
        self.profile_activated = not was_empty_field

        # self.latitude =
        # self.longitude =

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class UserTag(ManagedModel, TimeStampedModel, GetById):
    user = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь", on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag, blank=False, null=False, verbose_name="Тег", on_delete=models.CASCADE
    )

    objects_ = UserTagManager()

    class Meta:
        verbose_name = "Тег пользователя"
        verbose_name_plural = "Теги пользователя"
        unique_together = ('user', 'tag')


class UserPhoto(ManagedModel, TimeStampedModel, GetById):
    title = models.CharField(_('название'), max_length=32, blank=True, null=False)
    image = models.ImageField(_('изображение'), upload_to='images/', blank=False, null=False)
    main = models.BooleanField(_('главное'), default=False, blank=False, null=False)
    user = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь", on_delete=models.CASCADE
    )

    objects_ = UserPhotoManager()

    def __str__(self):
        return self.title

    def thumbnail_tag(self):
        return get_thumb(self.image, 0, 100)

    thumbnail_tag.short_description = 'Превью'

    def thumbnail_tag_icon(self):
        return get_thumb(self.image, 50, 0)

    thumbnail_tag_icon.short_description = 'Превью1'

    def list_thumbnail_tag(self):
        return get_thumb(self.image, 100, 0)

    list_thumbnail_tag.short_description = 'Превью'

    class Meta:
        verbose_name = 'Изображение пользователя'
        verbose_name_plural = 'Изображения пользователя'


class UsersConnect(ManagedModel, TimeStampedModel, GetById):
    """
    Connection means that user_1 likes user_2
    """

    PLUS = 'плюс'
    MINUS = 'минус'
    TYPES = Choices(
        (PLUS, "plus"), (MINUS, "minus")
    )
    type = models.CharField(_('тип'), max_length=32, choices=TYPES, default=PLUS)
    user_1 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 1", on_delete=models.CASCADE,
        related_name='user_1_set'
    )
    user_2 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 2", on_delete=models.CASCADE,
        related_name='user_2_set'
    )

    objects_ = UsersConnectManager()

    class Meta:
        verbose_name = "Коннект пользователей"
        verbose_name_plural = "Коннекты пользователей"
        unique_together = ('user_1', 'user_2')


class UsersFake(ManagedModel, TimeStampedModel, GetById):
    """
    Connection means that user_1 faked user_2
    """

    user_1 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 1", on_delete=models.CASCADE,
        related_name='user_fake_1_set'
    )
    user_2 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 2", on_delete=models.CASCADE,
        related_name='user_fake_2_set'
    )

    objects_ = UsersFakeManager()

    class Meta:
        verbose_name = "Fake-коннект пользователей"
        verbose_name_plural = "Fake-коннекты пользователей"
        unique_together = ('user_1', 'user_2')


class UsersBlackList(ManagedModel, TimeStampedModel, GetById):
    """
    Connection means that user_1 blacklisted user_2
    """

    user_1 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 1", on_delete=models.CASCADE,
        related_name='user_blacklist_1_set'
    )
    user_2 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 2", on_delete=models.CASCADE,
        related_name='user_blacklist_2_set'
    )

    objects_ = UsersBlackListManager()

    class Meta:
        verbose_name = "BlackList-коннект пользователей"
        verbose_name_plural = "BlackList-коннекты пользователей"
        unique_together = ('user_1', 'user_2')


class UsersRating(ManagedModel, TimeStampedModel, GetById):
    """
    Connection means that user_1 has rating N for user_2
    """

    user_1 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 1", on_delete=models.CASCADE,
        related_name='user_rating_1_set'
    )
    user_2 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 2", on_delete=models.CASCADE,
        related_name='user_rating_2_set'
    )
    rating = models.FloatField(_('рейтинг'), default=0.0)

    objects_ = UsersRatingManager()

    class Meta:
        verbose_name = "Rating-коннект пользователей"
        verbose_name_plural = "Rating-коннекты пользователей"
        unique_together = ('user_1', 'user_2')


class Notification(ManagedModel, TimeStampedModel, GetById):
    """
    Connection means that user_1 made smth to user_2
    """

    LIKE = 'лайк'
    PROFILE = 'просмотр профиля'
    MESSAGE = 'сообщение'
    LIKE_BACK = 'лайк в ответ'
    IGNORE = 'разрывание коннекта'
    TYPES = Choices(
        (LIKE, "like"), (PROFILE, "profile"), (MESSAGE, "message"), (LIKE_BACK, "like back"),
        (IGNORE, "ignore")
    )
    type = models.CharField(_('тип'), max_length=32, choices=TYPES)
    user_1 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 1", on_delete=models.CASCADE,
        related_name='user_notification_1_set'
    )
    user_2 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 2", on_delete=models.CASCADE,
        related_name='user_notification_2_set'
    )
    was_read = models.BooleanField(_('оповещение прочитано'), blank=False, null=False, default=False)

    objects_ = NotificationManager()

    class Meta:
        verbose_name = "Notification-коннект пользователей"
        verbose_name_plural = "Notification-коннекты пользователей"


class Message(ManagedModel, TimeStampedModel, GetById):
    """
    str(user_1.id) <= str(user_2.id)
    """

    TO_1_2 = '1 -> 2'
    TO_2_1 = '2 -> 1'
    TYPES = Choices((TO_1_2, '1 -> 2'), (TO_2_1, '2 -> 1'))
    type = models.CharField(_('тип'), max_length=32, choices=TYPES)
    user_1 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 1", on_delete=models.CASCADE,
        related_name='user_message_1_set'
    )
    user_2 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 2", on_delete=models.CASCADE,
        related_name='user_message_2_set'
    )
    message = models.CharField(_('сообщение'), max_length=256, blank=False, null=False)

    objects_ = MessageManager()

    class Meta:
        verbose_name = "Message-коннект пользователей"
        verbose_name_plural = "Message-коннекты пользователей"
