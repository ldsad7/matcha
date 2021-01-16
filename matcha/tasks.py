import logging

import mpu

from dating_site.celery import app
from dating_site.settings import verbose_flag, MAX_RATING

LOG = logging.getLogger(__name__)


def count_user_rating(user):
    from matcha.models import UsersConnect, UsersBlackList, UsersFake, UserPhoto, UserTag

    users_connects = UsersConnect.objects_.all()
    rating = \
        sum([1 for obj in users_connects if obj.user_2_id == user.id and obj.type == UsersConnect.PLUS]) - \
        sum([1 for obj in users_connects if obj.user_2_id == user.id and obj.type == UsersConnect.MINUS]) - \
        len(UsersBlackList.objects_.filter(user_2_id=user.id)) - \
        len(UsersFake.objects_.filter(user_2_id=user.id)) + \
        10 * int(user.profile_activated) + \
        5 * (len(UserPhoto.objects_.filter(user_id=user.id)) > 2) + \
        5 * (len(UserTag.objects_.filter(user_id=user.id)) > 2) + \
        sum([1 for obj in users_connects if obj.user_1_id == user.id])
    if rating < 0:
        rating = 0.0
    return rating


def sync_user_rating(user):
    """
    Counts fame rating of a user
    """

    from dating_site.settings import verbose_flag

    user.rating = min(count_user_rating(user), MAX_RATING)
    if verbose_flag:
        print(f"{user.id}: {user.rating}")
    user.save()


@app.task
def sync_rating():
    """
    Counts fame rating of all users
    """

    from matcha.models import User

    for user in User.objects_.all():
        sync_user_rating(user)


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


def ignore_only_blocked_and_faked_users_bidir(objs, user_id):
    """
    Removes blocked and faked users and himself from a list (bidirectional)
    """

    from matcha.models import UsersBlackList, UsersFake

    ignored_ids = {user_id}
    users_black_lists = UsersBlackList.objects_.all()
    ignored_ids |= {obj.user_2_id for obj in users_black_lists if obj.user_1_id == user_id}
    ignored_ids |= {obj.user_1_id for obj in users_black_lists if obj.user_2_id == user_id}

    users_fakes = UsersFake.objects_.all()
    ignored_ids |= {obj.user_2_id for obj in users_fakes if obj.user_1_id == user_id}
    ignored_ids |= {obj.user_1_id for obj in users_fakes if obj.user_2_id == user_id}

    users = [obj for obj in objs if obj.id not in ignored_ids]
    return users


def ignore_only_blocked_and_faked_users_onedir(objs, user_id):
    """
    Removes blocked and faked users and himself from a list (one direction)
    """
    from matcha.models import UsersBlackList, UsersFake

    ignored_ids = {user_id}
    users_black_lists = UsersBlackList.objects_.all()
    ignored_ids |= {obj.user_2_id for obj in users_black_lists if obj.user_1_id == user_id}

    users_fakes = UsersFake.objects_.all()
    ignored_ids |= {obj.user_2_id for obj in users_fakes if obj.user_1_id == user_id}

    users = [obj for obj in objs if obj.id not in ignored_ids]
    return users


def ignore_by_orientation_and_gender(users, user):
    from matcha.models import User
    if user.gender != User.UNKNOWN:
        if user.orientation == User.HETERO:
            users = [
                inner_user for inner_user in users
                if inner_user.gender not in [user.gender, User.UNKNOWN] and
                   inner_user.orientation not in [User.HOMO, User.UNKNOWN]
            ]
        elif user.orientation == User.HOMO:
            users = [
                inner_user for inner_user in users
                if inner_user.gender == user.gender and
                   inner_user.orientation not in [User.HETERO, User.UNKNOWN]
            ]
        elif user.orientation in [User.BI, User.UNKNOWN]:
            users = [
                inner_user for inner_user in users
                if (inner_user.gender == user.gender and
                    inner_user.orientation in [User.BI, User.HOMO]) or
                   (inner_user.gender not in [user.gender, User.UNKNOWN] and
                    inner_user.orientation in [User.BI, User.HETERO])
            ]
    elif user.orientation in [User.BI, User.UNKNOWN]:
        users = [
            inner_user for inner_user in users
            if inner_user.orientation in [User.BI, User.UNKNOWN]
        ]
    return users


def update_rating(users, user):
    from matcha.models import UserTag, UsersRating

    max_rating = 0.0
    max_distance = 0.0
    user_tags = set(user_tag.tag.name for user_tag in UserTag.objects_.filter(user_id=user.id))
    if user.latitude or user.longitude:
        check_coords = True
    else:
        check_coords = False
        max_distance = 1.0
    for inner_user in users:
        max_rating = min(max(inner_user.rating, max_rating), MAX_RATING)
        inner_user.tag_names = set(
            user_tag.tag.name for user_tag in UserTag.objects_.filter(user_id=inner_user.id)
        )
        if check_coords:
            if inner_user.latitude or inner_user.longitude:
                inner_user.distance = mpu.haversine_distance(
                    (user.latitude, user.longitude), (inner_user.latitude, inner_user.longitude)
                )
            else:
                if user.location.lower().strip() == inner_user.location.lower().strip():
                    inner_user.distance = 0
                else:
                    inner_user.distance = max_distance
            max_distance = max(inner_user.distance, max_distance)
        else:
            if user.location.lower().strip() == inner_user.location.lower().strip():
                inner_user.distance = 0
            else:
                inner_user.distance = 1
    for inner_user in users:
        users_rating = UsersRating.objects_.filter(user_1_id=inner_user.id, user_2_id=user.id)
        rating = \
            0.25 * inner_user.rating / (max_rating + 0.01) + \
            0.25 * len(user_tags & inner_user.tag_names) / (len(user_tags | inner_user.tag_names) + 0.01) + \
            0.5 * (1 - inner_user.distance / (max_distance + 0.01))
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
