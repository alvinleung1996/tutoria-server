import json

from django.contrib.auth.views import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.views import View

from .apiresponse import ApiResponse

# https://docs.djangoproject.com/en/1.11/topics/auth/default/#authentication-in-web-requests


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ApiResponse(error=dict(message='Unsupported request body encoding'))

        if ('username' not in data) or ('password' not in data):
            return ApiResponse(error=dict(message='Missing required data in request body'))

        if request.user.is_authenticated and request.user.username == data['username']:
            return ApiResponse(dict(message='already login'))

        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            return ApiResponse(error=dict(message='Wrong authentication information'))

        login(request, user)
        return ApiResponse(dict(message='Login success'))



class LogoutView(View):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            return ApiResponse(dict(message='logout Success'))

        else:
            return ApiResponse(dict(message='Already logout out'))
