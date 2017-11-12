import json
from decimal import Decimal
from datetime import timedelta
from http import HTTPStatus

from dateutil import parser

from django.contrib.auth.views import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.http import HttpResponse

from ..models import User, Student, Tutor, Company, Tutorial, UnavailablePeriod

from .api_response import ApiResponse

# https://docs.djangoproject.com/en/1.11/topics/auth/default/#authentication-in-web-requests

def _user_to_json(user):
    json = dict(
        username = user.username,
        givenName = user.given_name,
        familyName = user.family_name,
        fullName = user.full_name,
        phoneNumber = user.phone_number,
        email = user.email,
        roles = [],
        avatar = user.avatar
        # TODO: more data
    )
    for role in user.roles:
        if isinstance(role, Student):
            json['roles'].append('student')
        elif isinstance(role, Tutor):
            json['roles'].append('tutor')
        elif isinstance(role, Company):
            json['roles'].append('company')

    return json

class ProfileView(View):

    http_method_names = ['get']

    # def head(self, request, username, *args, **kwargs):

    #     if (not request.user.is_authenticated
    #             or not request.user.is_active
    #             or (username != 'me' and request.user.username != username)):
    #         return HttpResponse(status=HTTPStatus.FORBIDDEN)

    #     try:
    #         # request.user is django.contrib.auth.models.User
    #         # request.user.user is tutoriaapi.models.User
    #         user = request.user.user
    #     except User.DoesNotExist:
    #         return HttpResponse(status=404)

    #     # return status code = 200
    #     return HttpResponse()


    def get(self, request, username, *args, **kwargs):

        if not request.user.is_authenticated:
            return ApiResponse(error_message='Not authenticated', status=HTTPStatus.UNAUTHORIZED)

        elif not request.user.is_active:
            return ApiResponse(error_message='Not active', status=HTTPStatus.UNAUTHORIZED)
        
        elif username != 'me' and request.user.username != username:
            return ApiResponse(error_message='Access forbidened', status=HTTPStatus.FORBIDDEN)
            
        try:
            # request.user is django.contrib.auth.models.User
            # request.user.user is tutoriaapi.models.User
            user = request.user.user
        except User.DoesNotExist:
            return ApiResponse(error_message='No user profile found', status=HTTPStatus.INTERNAL_SERVER_ERROR)

        response = _user_to_json(user)
        return ApiResponse(data=response)
    


@method_decorator(csrf_exempt, name='dispatch')
class LoginSessionView(View):

    http_method_names = ['put', 'delete']

    def put(self, request, username, *args, **kwargs):

        if request.user.is_authenticated:
            if username == 'me' or username == request.user.username:
                try:
                    user = request.user.user
                except User.DoesNotExist:
                    return ApiResponse(error_message='No user profile found', status=HTTPStatus.INTERNAL_SERVER_ERROR)
                response = _user_to_json(user)
                return ApiResponse(data=response)
            else:
                logout(request)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ApiResponse(error_message='Invalid login data', status=HTTPStatus.BAD_REQUEST)

        if 'password' not in data:
            return ApiResponse(error_message='Password required', status=HTTPStatus.BAD_REQUEST)
        
        base_user = authenticate(username=username, password=data['password'])
        if base_user is None:
            return ApiResponse(error_message='Wrong login information', status=HTTPStatus.UNAUTHORIZED)

        if not base_user.is_active:
            return ApiResponse(error_message='User not active', status=HTTPStatus.UNAUTHORIZED)

        try:
            user = base_user.user
        except User.DoesNotExist:
            return ApiResponse(error_message='No user profile found', status=HTTPStatus.INTERNAL_SERVER_ERROR)

        login(request, base_user)
        
        response = _user_to_json(user)
        return ApiResponse(data=response)


    def delete(self, request, username, *args, **kwargs):
        if not request.user.is_authenticated:
            return ApiResponse(message='Not logged in')

        elif username != 'me' and username != request.user.username:
            return ApiResponse(error_message='Delete forbidened', status=HTTPStatus.FORBIDDEN)

        logout(request)
        return ApiResponse(message='Logout success')



class EventsView(View):

    http_method_names = ['get']

    def get(self, request, username, *args, **kwargs):

        if (not request.user.is_authenticated or not request.user.is_active
            or (username != 'me' and request.user.username != username)):
            return ApiResponse(message='Login required', status=HTTPStatus.FORBIDDEN)
        
        try:
            user = request.user.user
        except User.DoesNotExist:
            return ApiResponse(message='Profile not found', status=404)

        data = []
        
        for event in user.event_set.filter(cancelled=False):
            concrete_event = event.concrete_event

            item = dict(
                id = concrete_event.id,
                startTime = concrete_event.start_time.isoformat(timespec='microseconds'),
                endTime = concrete_event.end_time.isoformat(timespec='microseconds')
            )

            if isinstance(concrete_event, Tutorial):
                item['type'] = 'tutorial'
                item['student'] = dict(
                    givenName = concrete_event.student.user.given_name,
                    familyName = concrete_event.student.user.family_name
                )
                item['tutor'] = dict(
                    givenName = concrete_event.tutor.user.given_name,
                    familyName = concrete_event.tutor.user.family_name
                )

            elif isinstance(concrete_event, UnavailablePeriod):
                item['type'] = 'unavailablePeriod'
                item['tutor'] = dict(
                    givenName = concrete_event.tutor.user.given_name,
                    familyName = concrete_event.tutor.user.family_name
                )
            
            data.append(item)

        return ApiResponse(dict(data=data))


@method_decorator(csrf_exempt, name='dispatch')
class TutorialCollectionView(View):

    http_method_names = ['post']

    def post(self, request, username, *args, **kwargs):
        if (not request.user.is_authenticated or not request.user.is_active
                or (username != 'me' and request.user.username != username)):
            return ApiResponse(message='Login required', status=HTTPStatus.FORBIDDEN)
        
        try:
            student = Student.objects.get(user__base_user=request.user)
        except Student.DoesNotExist:
            return ApiResponse(message='Require student role', status=403)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return ApiResponse(message='Cannot recognize data', status=HTTPStatus.BAD_REQUEST)

        if 'tutorUsername' not in data or 'startTime' not in data or 'endTime' not in data:
            return ApiResponse(message='Data missing', status=HTTPStatus.BAD_REQUEST)

        try:
            tutor = Tutor.objects.get(user__username=data['tutorUsername'])
        except Tutor.DoesNotExist:
            return ApiResponse(message='Does not have tutor role', status=HTTPStatus.FORBIDDEN)

        try:
            start_time = parser.parse(data['startTime'])
            end_time = parser.parse(data['endTime'])
        except (ValueError, OverflowError):
            return ApiResponse(message='Wrong time format', status=HTTPStatus.BAD_REQUEST)
        
        # TODO: Calc charge...
        duration = end_time - start_time
        charge = tutor.hourly_rate * Decimal(duration / timedelta(hours=1))

        # TODO: Check time slow availability
        pass

        if 'preview' in data and bool(data['preview']):
            return ApiResponse(dict(
                charge = charge
            ))
        
        else:
            tutorial = student.add_tutorial(
                tutor = tutor,
                start_time = start_time,
                end_time = end_time
            )
            return ApiResponse(dict(
                tutorialId=tutorial.id
            ))



@method_decorator(csrf_exempt, name='dispatch')
class TutorialView(View):

    http_method_names = ['delete']
    
    def delete(self, request, username, tutorial_id, *args, **kwargs):
        if (not request.user.is_authenticated or not request.user.is_active
                or (username != 'me' and request.user.username != username)):
            return ApiResponse(message='Login required', status=HTTPStatus.FORBIDDEN)
        
        try:
            tutorial = Tutorial.objects.get(id=tutorial_id, student__user__base_user=request.user)
        except Tutorial.DoesNotExist:
            return ApiResponse(message='Cannot find event with id: {id}'.format(id=tutorial_id), status=HTTPStatus.NOT_FOUND)

        if tutorial.cancelled:
            return ApiResponse(message='Tutorial has already been cancelled')
        
        tutorial.cancelled = True
        tutorial.save()
        
        return ApiResponse(message='Success')
        