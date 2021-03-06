import json
from datetime import datetime

import requests
# from django.contrib.gis.geoip2 import GeoIP2
from django.http import Http404

from dating_site.settings import verbose_flag
from matcha.models import UsersConnect, Notification, User

IP_TO_JSON = {}


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
            user_obj = User.objects_.get(id=user_1_id)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            ip_2 = requests.get('https://api.ipify.org/?format=json').json().get('ip')
            if ip == '127.0.0.1' or ip != ip_2:
                ip = ip_2
            if verbose_flag:
                print(f'ip: {ip}')
            try:
                if ip in IP_TO_JSON:
                    data = IP_TO_JSON[ip]
                else:
                    data = requests.get(f"https://extreme-ip-lookup.com/json/{ip}").json()
                    IP_TO_JSON[ip] = data
            except Exception as e:
                data = {}
            try:
                user_obj.country = data.get('country') or None
                user_obj.city = data.get('city') or None
                latitude, longitude = data.get("lat") or 0.0, data.get("lon") or 0.0
                latitude, longitude = list(
                    map(float, [latitude, longitude])
                )
                if -90 <= latitude <= 90 and -180 <= longitude <= 180:
                    user_obj.latitude = latitude
                    user_obj.longitude = longitude
            except Exception as e:
                if verbose_flag:
                    print(f"Error happened: {e}")
            user_obj.last_online = datetime.utcnow()
            user_obj.save(model_fields=['last_online', 'latitude', 'longitude'])

            if path.startswith('/api/v1/user_connects/'):
                try:
                    body = request.body.decode()
                    body = json.loads(body)
                except Exception as e:
                    print(f'error happened: {e}')
                    body = {}
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
                if User.objects_.get(id=user_2_id) is None:
                    raise Http404(f"Пользователя с данным id ({user_2_id}) не существует в базе")
                if user_1_id != user_2_id:
                    if method == 'GET':
                        Notification(
                            user_1_id=user_1_id,
                            user_2_id=user_2_id,
                            type=Notification.PROFILE
                        ).save()

        response = self.get_response(request)

        return response
