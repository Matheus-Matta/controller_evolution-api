from django.shortcuts import redirect
from django.conf import settings

class Redirect404ToLogin: # apenas quando debug estiver false
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code == 404:
            return redirect(settings.LOGIN_URL)

        return response
