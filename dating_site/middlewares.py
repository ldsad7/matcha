import json
from datetime import datetime

import pytz
from django.http import Http404
from django.contrib.gis.geoip2 import GeoIP2

from matcha.models import UsersConnect, Notification, User


class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        method = request.method
        path = request.path
        user_1_id = request.user.id
        if user_1_id is not None:
            try:
                body = request.body.decode()
                body = json.loads(body)
            except Exception:
                body = []

            user_obj = User.objects_.get(id=user_1_id)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            print(f'ip: {ip}')
            g = GeoIP2()
            ip = '205.186.163.125'  # TODO: REPLACE HARDCODE LATER
            user_obj.country = g.country(ip)['country_name']
            user_obj.city = g.city(ip)['city']
            user_obj.latitude, user_obj.longitude = g.lat_lon(ip)
            user_obj.last_login = datetime.utcnow()
            user_obj.save()

            if path.startswith('/api/v1/user_connects/'):
                if method == 'POST':
                    if body['type'] == UsersConnect.PLUS:
                        Notification(
                            user_1_id=user_1_id,
                            user_2_id=body['user_2_id'],
                            type=Notification.LIKE
                        ).save()
                elif method == 'PATCH':
                    if body['type'] == UsersConnect.PLUS:
                        type_ = Notification.LIKE_BACK
                    else:
                        type_ = Notification.IGNORE
                    Notification(
                        user_1_id=user_1_id,
                        user_2_id=UsersConnect.objects_.get(id=path.split('/')[-2]).user_2.id,
                        type=type_
                    ).save()
            elif path.startswith('/profiles/'):
                user_2_id = path.split('/')[-2]
                try:
                    user_2_id = int(user_2_id)
                except ValueError:
                    raise Http404(f"Пользователя с данным id ({user_2_id}) не существует в базе")
                if user_1_id != user_2_id:
                    if method == 'GET':
                        Notification(
                            user_1_id=user_1_id,
                            user_2_id=path.split('/')[-2],
                            type=Notification.PROFILE
                        ).save()

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
