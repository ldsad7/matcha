from datetime import datetime, date, timedelta

from django.db.models import Q
from django_filters import rest_framework as filters
from .models import User, UserTag
from .exceptions import IncorrectArgument


class UserFilter(filters.FilterSet):
    age = filters.CharFilter('age', method='filter_age')
    rating = filters.CharFilter('rating', method='filter_rating')
    location = filters.CharFilter('location', method='filter_location')
    tags = filters.CharFilter('tags', method='filter_tags')

    def filter_age(self, queryset, name, value):
        try:
            low, high = list(map(int, value.split(':')))
        except Exception:
            raise IncorrectArgument
        today = date.today()
        return queryset.filter(
            date_of_birth__gte=date(year=today.year - high - 1, month=today.month, day=today.day),
            date_of_birth__lte=date(year=today.year - low, month=today.month, day=today.day)
        )

    def filter_rating(self, queryset, name, value):
        try:
            low, high = list(map(float, value.replace(',', '.').split(':')))
        except Exception:
            raise IncorrectArgument
        ids = [obj.id for obj in queryset if low <= obj.rating <= high]
        return queryset.filter(id__in=ids)

    def filter_location(self, queryset, name, value):
        """
        TODO: rewrite with latitude, longitude?
        """
        return queryset.filter(
            Q(**{'__'.join([name, 'icontains']): value}) | Q(**{'__'.join([name, 'in']): value})
        )

    def filter_tags(self, queryset, name, value):
        tag_names = value.split(',')
        user_ids = [obj.user.id for obj in UserTag.objects.filter(
            tag__name__in=tag_names
        )]
        return queryset.filter(id__in=user_ids)
