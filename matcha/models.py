from django.db import models
from model_utils.models import TimeStampedModel
from django.contrib.auth.models import AbstractUser
from model_utils import Choices
from django.utils.translation import ugettext_lazy as _
from .common import get_by_model_and_id, get_thumb


class Tag(TimeStampedModel):
    name = models.CharField(_('название'), max_length=32, blank=False, null=False)

    def get_by_id(self, _id):
        return get_by_model_and_id(self, _id)

    def __str__(self):
        return f"Tag {self.name}"

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class User(AbstractUser):
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

    def get_by_id(self, _id):
        return get_by_model_and_id(self, _id)

    def save(self, *args, **kwargs):
        print(f'args: {args}')
        print(f'kwargs: {kwargs}')
        was_empty_field = False
        for field in self._meta.fields:
            name = field.name
            value = getattr(self, field.name)
            if (name in ['first_name', 'last_name', 'info', 'location', 'date_of_birth'] and not value) or \
                    (name in ['gender', 'orientation'] and value == self.UNKNOWN):
                was_empty_field = True
                break
        self.profile_activated = not was_empty_field
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class UserTag(TimeStampedModel):
    user = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь", on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag, blank=False, null=False, verbose_name="Тег", on_delete=models.CASCADE
    )

    def get_by_id(self, _id):
        return get_by_model_and_id(self, _id)

    class Meta:
        verbose_name = "Тег пользователя"
        verbose_name_plural = "Теги пользователя"
        unique_together = ('user', 'tag')


class UserPhoto(TimeStampedModel):
    title = models.CharField(_('название'), max_length=32, blank=True, null=False)
    image = models.ImageField(_('изображение'), upload_to='images/', blank=False, null=False)
    user = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title

    def get_by_id(self, _id):
        return get_by_model_and_id(self, _id)

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


class UsersConnect(TimeStampedModel):
    """
    Connection means that user_1 likes user_2
    """

    user_1 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 1", on_delete=models.CASCADE,
        related_name='user_1_set'
    )
    user_2 = models.ForeignKey(
        User, blank=False, null=False, verbose_name="Пользователь 2", on_delete=models.CASCADE,
        related_name='user_2_set'
    )

    def get_by_id(self, _id):
        return get_by_model_and_id(self, _id)

    class Meta:
        verbose_name = "Коннект пользователей"
        verbose_name_plural = "Коннекты пользователей"
        unique_together = ('user_1', 'user_2')
