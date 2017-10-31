from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout

import json

from .apiresponse import ApiResponse

# https://docs.djangoproject.com/en/1.11/topics/auth/default/#authentication-in-web-requests

@csrf_exempt
def authLogin(request):

    if request.method != 'POST':
        return ApiResponse(error=dict(message='Unsupported request method'))

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



@csrf_exempt
def authLogout(request):

    if request.user.is_authenticated:
        logout(request)
        return ApiResponse(dict(message='logout Success'))

    else:
        return ApiResponse(dict(message='Already logout out'))
