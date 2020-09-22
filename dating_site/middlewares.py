from matcha.models import UsersConnect


class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        print(f'request.method: {request.method}')
        print(f'request.path: {request.path}')
        print(f'request.user: {request.user.id}')

        if request.method == 'DELETE':
            id_ = request.path.split('/')[-2]
            print(f'{id_}, {UsersConnect.objects_.filter(id=id_)}')

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
