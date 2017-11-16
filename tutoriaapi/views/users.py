import json
from decimal import Decimal
from datetime import timedelta, datetime, timezone
from http import HTTPStatus

from dateutil import parser

from django.contrib.auth.views import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.views import View

from ..models import User, Student, Tutor, Company, Tutorial, UnavailablePeriod, Transaction
from ..utils.time_utils import get_time

from .api_response import ApiResponse

from django.db.models import Q

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

class UserView(View):

    http_method_names = ['get']

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
class UserLoginSessionView(View):

    http_method_names = ['put', 'delete']

    def put(self, request, username, *args, **kwargs):

        if request.user.is_authenticated:
            if username == 'me' or username == request.user.username:
                try:
                    user = request.user.user
                except User.DoesNotExist:
                    return ApiResponse(error_message='No user profile found', status=HTTPStatus.INTERNAL_SERVER_ERROR)

                return ApiResponse(message='Already logged in')
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
        
        return ApiResponse(message='login success')


    def delete(self, request, username, *args, **kwargs):
        if not request.user.is_authenticated:
            return ApiResponse(message='Not logged in')

        elif username != 'me' and username != request.user.username:
            return ApiResponse(error_message='Delete forbidened', status=HTTPStatus.FORBIDDEN)

        logout(request)
        return ApiResponse(message='Logout success')



class UserEventsView(View):

    http_method_names = ['get']

    def get(self, request, username, *args, **kwargs):

        if (not request.user.is_authenticated or not request.user.is_active
            or (username != 'me' and request.user.username != username)):
            return ApiResponse(error_message='Login required', status=HTTPStatus.FORBIDDEN)
        
        try:
            user = request.user.user
        except User.DoesNotExist:
            return ApiResponse(error_message='Profile not found', status=HTTPStatus.INTERNAL_SERVER_ERROR)

        data = []
        
        for event in user.event_set.filter(
            cancelled = False,
            start_time__gte = get_time(hour=0, minute=0)    
        ):
            concrete_event = event.concrete_event

            if isinstance(concrete_event, Tutorial):
                event_type = 'tutorial'
            elif isinstance(concrete_event, UnavailablePeriod):
                event_type = 'unavailablePeriod'
            else:
                event_type = 'unknown'

            item = dict(
                id = event.id,
                startTime = event.start_time.isoformat(timespec='microseconds'),
                endTime = event.end_time.isoformat(timespec='microseconds'),
                type = event_type
            )
            data.append(item)

        return ApiResponse(data=data)

class UserTransactionsView(View):

    http_method_names = ['get']

    def get(self, request, username, *args, **kwargs):

        if (not request.user.is_authenticated or not request.user.is_active
            or (username != 'me' and request.user.username != username)):
            return ApiResponse(error_message='Login required', status=HTTPStatus.FORBIDDEN)
        
        try:
            user = request.user.user
        except User.DoesNotExist:
            return ApiResponse(error_message='Profile not found', status=HTTPStatus.INTERNAL_SERVER_ERROR)

        data = []

        for transaction in Transaction.objects.filter(
            Q(withdraw_wallet=user.wallet) | Q(deposit_wallet=user.wallet),
            time__gte=datetime.now(tz=timezone.utc)-timedelta(days=30)
        ).order_by('-time'):
        # '-' for descending order
            item = dict(
                time = transaction.time.isoformat(timespec='microseconds'),
                amount = str(transaction.amount)
            )
            if transaction.withdraw_wallet is not None:
                item['withdrawFrom'] = transaction.withdraw_wallet.user.full_name
            if transaction.deposit_wallet is not None:
                item['depositTo'] = transaction.deposit_wallet.user.full_name
            data.append(item)
        return ApiResponse(data=data)

@method_decorator(csrf_exempt, name='dispatch')
class UserWalletsView(View):

    http_method_names = ['post']

    def post(self, request, username, *args, **kwargs):

        if (not request.user.is_authenticated or not request.user.is_active
            or (username != 'me' and request.user.username != username)):
            return ApiResponse(error_message='Login required', status=HTTPStatus.FORBIDDEN)
        
        try:
            user = request.user.user
        except User.DoesNotExist:
            return ApiResponse(error_message='Profile not found', status=HTTPStatus.INTERNAL_SERVER_ERROR)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ApiResponse(error_message='Invalid data', status=HTTPStatus.BAD_REQUEST)

        if 'amount' not in data:
            return ApiResponse(error_message='Amount required', status=HTTPStatus.BAD_REQUEST)
        
        changeAmount = Decimal(data['amount'])

        if changeAmount == Decimal('0'):
            return ApiResponse(error_message='Amount required', status=HTTPStatus.BAD_REQUEST)

        if changeAmount > Decimal('0'):
            Transaction.create(
                withdraw = None,
                deposit = user,
                amount = abs(changeAmount)
            )
            return ApiResponse(message='deposit success')
        else:
            try:
                Transaction.create(
                    withdraw = user,
                    deposit = None,
                    amount = abs(changeAmount)
                )
                return ApiResponse(message='withdraw success')
            except user.wallet.InsufficientBalanceError:
                return ApiResponse(error_message='Insufficient balance error', status=HTTPStatus.INTERNAL_SERVER_ERROR)