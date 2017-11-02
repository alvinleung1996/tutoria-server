import json

from django.contrib.auth.views import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.views import View

from ..models import User

from .api_response import ApiResponse

# https://docs.djangoproject.com/en/1.11/topics/auth/default/#authentication-in-web-requests

def _user_to_json(user):
    json = dict(
        username = user.username,
        givenName = user.given_name,
        familyName = user.family_name,
        avatar = user.avatar
        # TODO: more data
    )
    return json

class ProfileView(View):

    http_method_names = ['get']

    def get(self, request, username, *args, **kwargs):

        if not request.user.is_authenticated:
            return ApiResponse(message='Not authenticated', status_code=403)

        elif not request.user.is_active:
            return ApiResponse(message='Not active', status_code=403)
        
        elif username != 'me' and request.user.username != username:
            return ApiResponse(message='Access forbidened', status_code=403)
            
        try:
            # request.user is django.contrib.auth.models.User
            # request.user.user is tutoriaapi.models.User
            user = request.user.user
        except User.DoesNotExist:
            return ApiResponse(message='No user profile found', status_code=404)

        response = _user_to_json(user)
        return ApiResponse(response)
    


@method_decorator(csrf_exempt, name='dispatch')
class LoginSessionView(View):

    http_method_names = ['put', 'delete']

    def put(self, request, username, *args, **kwargs):

        if request.user.is_authenticated:
            if username == 'me' or username == request.user.username:
                try:
                    user = request.user.user
                except User.DoesNotExist:
                    return ApiResponse(message='No user profile found', status_code=404)
                response = _user_to_json(user)
                return ApiResponse(response)
            else:
                logout(request)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ApiResponse(message='Invalid login data', status_code=403)

        try:
            password = data['password']
        except KeyError:
            return ApiResponse(message='Password required', status_code=403)
        
        base_user = authenticate(username=username, password=password)
        if base_user is None:
            return ApiResponse(message='Wrong login information', status_code=404)

        if not base_user.is_active:
            return ApiResponse(message='User not active', status_code=403)

        try:
            user = base_user.user
        except User.DoesNotExist:
            return ApiResponse(message='No user profile found', status_code=404)
        
        response = _user_to_json(user)
        return ApiResponse(response)


    def delete(self, request, username, *args, **kwargs):
        if not request.user.is_authenticated:
            return ApiResponse(message='Not logged in')

        elif username != 'me' and username != request.user.username:
            return ApiResponse(message='Delete forbidened', status_code=403)

        logout(request)
        return ApiResponse(message='Logout success')
