from datetime import date
import pytz

from .models import UserTag, Tag
from .exceptions import IncorrectArgument


def filter_age(queryset, value, model):
    try:
        low, high = list(map(int, value.split(':')))
    except Exception:
        # raise IncorrectArgument
        return queryset
    today = date.today()

    ids = [obj.id for obj in queryset]
    return model.objects_.filter(
        id__in=ids,
        date_of_birth__gte=date(year=today.year - high - 1, month=today.month, day=today.day),
        date_of_birth__lte=date(year=today.year - low, month=today.month, day=today.day)
    )


def filter_rating(queryset, value, model):
    try:
        low, high = list(map(float, value.replace(',', '.').split(':')))
    except Exception:
        # raise IncorrectArgument
        return queryset
    ids = [obj.id for obj in queryset if low <= obj.rating <= high]
    return model.objects_.filter(id__in=ids)


def filter_location(queryset, value, model):
    """
    TODO: rewrite with latitude, longitude?
    """
    ids = [obj.id for obj in queryset]
    return model.objects_.filter(id__in=ids, location__icontains=value)


def filter_name(queryset, value, model):
    return [
        obj for obj in queryset
        if value.lower() in f'{obj.first_name} {obj.last_name}'.lower() or
           value.lower() in f'{obj.last_name} {obj.first_name}'.lower() or
           value.lower() in obj.username.lower()
    ]


def filter_tags(queryset, value, model):
    tag_names = value.split(',')
    tag_names = [tag_name for tag_name in tag_names if tag_name]
    if not tag_names:
        return queryset
    tag_ids = [obj.id for obj in Tag.objects_.filter(name__in=tag_names)]
    user_ids = [obj.user.id for obj in UserTag.objects_.filter(tag_id__in=tag_ids)]
    ids = {obj.id for obj in queryset}
    user_ids = ids & set(user_ids)
    return model.objects_.filter(id__in=user_ids)


def filter_timestamp(queryset, value):
    return [
        obj for obj in queryset if obj.created.replace(tzinfo=pytz.UTC).timestamp() >= value
    ]


# class UserFilter(filters.FilterSet):
#     age = filters.CharFilter('age', method='filter_age')
#     rating = filters.CharFilter('rating', method='filter_rating')
#     location = filters.CharFilter('location', method='filter_location')
#     tags = filters.CharFilter('tags', method='filter_tags')
#
#     def filter_age(self, queryset, name, value):
#         try:
#             low, high = list(map(int, value.split(':')))
#         except Exception:
#             raise IncorrectArgument
#         today = date.today()
#         return queryset.filter(
#             date_of_birth__gte=date(year=today.year - high - 1, month=today.month, day=today.day),
#             date_of_birth__lte=date(year=today.year - low, month=today.month, day=today.day)
#         )
#
#     def filter_rating(self, queryset, name, value):
#         try:
#             low, high = list(map(float, value.replace(',', '.').split(':')))
#         except Exception:
#             raise IncorrectArgument
#         ids = [obj.id for obj in queryset if low <= obj.rating <= high]
#         return queryset.filter(id__in=ids)
#
#     def filter_location(self, queryset, name, value):
#         """
#         TODO: rewrite with latitude, longitude?
#         """
#         return queryset.filter(Q(**{'__'.join([name, 'icontains']): value}))
#
#     def filter_tags(self, queryset, name, value):
#         tag_names = value.split(',')
#         user_ids = [obj.user.id for obj in UserTag.objects.filter(
#             tag__name__in=tag_names
#         )]
#         return queryset.filter(id__in=user_ids)
