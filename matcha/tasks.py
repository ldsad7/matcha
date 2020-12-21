import logging

from dating_site.celery import app

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
        user.rating = rating
        if verbose_flag:
            print(f"{user.id}: {user.rating}")
        user.save()
