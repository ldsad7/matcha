import logging

import mpu

from dating_site.celery import app
from dating_site.settings import verbose_flag, MAX_RATING

LOG = logging.getLogger(__name__)


@app.task
def sync_rating():
    from dating_site.settings import verbose_flag
    from matcha.models import User, UsersConnect, UsersBlackList, UsersFake, UserPhoto, UserTag
    for user in User.objects_.all():
        users_connects = UsersConnect.objects_.all()
        rating = \
            sum([1 for obj in users_connects if obj.user_2_id == user.id and obj.type == UsersConnect.PLUS]) - \
            sum([1 for obj in users_connects if obj.user_2_id == user.id and obj.type == UsersConnect.MINUS]) - \
            len(UsersBlackList.objects_.filter(user_2_id=user.id)) - \
            len(UsersFake.objects_.filter(user_2_id=user.id)) + \
            10 * int(user.profile_activated) + \
            5 * (len(UserPhoto.objects_.filter(user_id=user.id)) > 3) + \
            5 * (len(UserTag.objects_.filter(user_id=user.id)) > 3) + \
            sum([1 for obj in users_connects if obj.user_1_id == user.id])
        if rating < 0:
            rating = 0.0
        user.rating = min(rating, MAX_RATING)
        if verbose_flag:
            print(f"{user.id}: {user.rating}")
        user.save()


def ignore_false_users(objs, user_id):
    """
    Removes blocked, faked, already (dis)liked users and himself from a list
    """
    from matcha.models import UsersConnect, UsersBlackList, UsersFake

    ignored_ids = {user_id}

    users_connects = UsersConnect.objects_.all()
    ignored_ids |= {obj.user_2_id for obj in users_connects if obj.user_1_id == user_id}
    ignored_ids |= {obj.user_1_id for obj in users_connects if
                    obj.user_2_id == user_id and obj.type == UsersConnect.MINUS}

    users_black_lists = UsersBlackList.objects_.all()
    ignored_ids |= {obj.user_2_id for obj in users_black_lists if obj.user_1_id == user_id}
    ignored_ids |= {obj.user_1_id for obj in users_black_lists if obj.user_2_id == user_id}

    users_fakes = UsersFake.objects_.all()
    ignored_ids |= {obj.user_2_id for obj in users_fakes if obj.user_1_id == user_id}
    ignored_ids |= {obj.user_1_id for obj in users_fakes if obj.user_2_id == user_id}

    users = [obj for obj in objs if obj.id not in ignored_ids]
    return users


def ignore_by_orientation_and_gender(users, user):
    from matcha.models import User
    if user.gender != User.UNKNOWN and user.orientation != User.UNKNOWN:
        if user.orientation == User.HETERO:
            users = [
                inner_user for inner_user in users if inner_user.gender not in [user.gender, User.UNKNOWN]
            ]
        elif user.orientation == User.HOMO:
            users = [
                inner_user for inner_user in users if inner_user.gender == user.gender
            ]
        elif user.orientation == User.BI:
            users = [
                inner_user for inner_user in users if inner_user.gender != User.UNKNOWN
            ]
    return users


def update_rating(users, user):
    from matcha.models import UserTag, UsersRating

    max_rating = 0.0
    max_distance = 0.0
    user_tags = set(user_tag.tag.name for user_tag in UserTag.objects_.filter(user_id=user.id))
    for inner_user in users:
        max_rating = min(max(inner_user.rating, max_rating), MAX_RATING)
        inner_user.distance = mpu.haversine_distance(
            (user.latitude, user.longitude), (inner_user.latitude, inner_user.longitude)
        )
        max_distance = max(inner_user.distance, max_distance)
        inner_user.tag_names = set(
            user_tag.tag.name for user_tag in UserTag.objects_.filter(user_id=inner_user.id)
        )
    for inner_user in users:
        users_rating = UsersRating.objects_.filter(user_1_id=inner_user.id, user_2_id=user.id)
        rating = \
            0.33 * inner_user.rating / (max_rating + 0.01) + \
            0.33 * len(user_tags & inner_user.tag_names) / (len(user_tags | inner_user.tag_names) + 0.1) + \
            0.33 * (1 - inner_user.distance / (max_distance + 0.01))
        rating = min(rating, MAX_RATING)
        if users_rating:
            users_rating[0].rating = rating
        else:
            users_rating.append(UsersRating(
                user_1_id=inner_user.id, user_2_id=user.id, rating=rating
            ))
        users_rating[0].save()


@app.task
def sync_relfexive_rating():
    from matcha.models import User

    all_users = User.objects_.all()
    for user in all_users:
        users = ignore_false_users(all_users, user.id)
        users = ignore_by_orientation_and_gender(users, user)
        update_rating(users, user)
        if verbose_flag:
            print(f'RATING SAVED {user.id}')
