import json

from django.http import Http404

from matcha.models import UsersConnect, Notification


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
        body = request.body.decode()
        if body:
            body = json.loads(body)
        referer = request.headers.get('Referer')

        if path.startswith('/api/v1/user_connects/'):
            if method == 'DELETE':
                Notification(
                    user_1_id=user_1_id,
                    user_2_id=UsersConnect.objects_.get(id=path.split('/')[-2]).user_2.id,
                    type=Notification.IGNORE
                ).save()
            elif method == 'POST':
                if referer is not None and referer.endswith('/connections'):
                    type_ = Notification.LIKE_BACK
                else:
                    type_ = Notification.LIKE
                Notification(
                    user_1_id=user_1_id,
                    user_2_id=body['user_2_id'],
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
