import json
from decimal import Decimal
from datetime import timedelta, datetime, timezone
from http import HTTPStatus
import re

from dateutil import parser

from django.contrib.auth.views import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.views import View

from ..models import User, Student, Tutor, Company, Tutorial, UnavailablePeriod, Transaction, Wallet
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
        roles = ['user'],
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

@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):

    http_method_names = ['get', 'put']

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


    def put(self, request, username, *args, **kwargs):

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ApiResponse(error_message='Invalid body', status=HTTPStatus.BAD_REQUEST)
        
        error = dict()

        if (request.user.is_authenticated and request.user.is_active
                and (username == 'me' or request.user.username == username)):
            # User want to update his/her profile

            # if request.user.username != username:
            #     e = self.validate_username(data['username'])
            #     if e:
            #         error['username'] = e

            if 'password' in data:
                e = self.validate_password(data['password'])
                if e:
                    error['password'] = e

            if 'email' in data:
                e = self.validate_email(data['email'])
                if e:
                    error['email'] = e

            if 'givenName' in data:
                e = self.validate_given_name(data['givenName'])
                if e:
                    error['givenName'] = e

            if 'familyName' in data:
                e = self.validate_family_name(data['familyName'])
                if e:
                    error['familyName'] = e

            if 'phoneNumber' in data:
                e = self.validate_phone_number(data['phoneNumber'])
                if e:
                    error['phoneNumber'] = e

            if error:
                return ApiResponse(error=error, status=HTTPStatus.BAD_REQUEST)

            try:
                user = request.user.user
            except User.DoesNotExist:
                return ApiResponse(error_message='Cannot find user profile', status=HTTPStatus.INTERNAL_SERVER_ERROR)

            require_relogin = False

            # if username != 'me' and user.username != username:
            #     user.username = username

            if 'password' in data:
                user.set_password(data['password'])
                require_relogin = True

            if 'email' in data:
                user.email = data['email']

            if 'givenName' in data:
                user.given_name = data['givenName']

            if 'familyName' in data:
                user.family_name = data['familyName']

            if 'phoneNumber' in data:
                user.phone_number = data['phoneNumber']

            user.save()

            # If user has supply the password ('password' in data)
            # user will be logged out after set_password() (even if the password has not changed)
            if require_relogin:
                login(request, user)

            return ApiResponse(message='Update success')

        else:
            # User want to create a new account

            e = self.validate_username(username)
            if e:
                error['username'] = e

            if 'password' not in data:
                error['password'] = 'Password required'
            else:
                e = self.validate_password(data['password'])
                if e:
                    error['password'] = e

            if 'email' not in data:
                error['email'] = 'Email required'
            else:
                e = self.validate_email(data['email'])
                if e:
                    error['email'] = e

            if 'givenName' not in data:
                error['givenName'] = 'Given name required'
            else:
                e = self.validate_given_name(data['givenName'])
                if e:
                    error['givenName'] = e

            if 'familyName' not in data:
                error['familyName'] = 'Family name required'
            else:
                e = self.validate_family_name(data['familyName'])
                if e:
                    error['familyName'] = e

            if 'phoneNumber' not in data:
                error['phoneNumber'] = 'Phone number required'
            else:
                e = self.validate_phone_number(data['phoneNumber'])
                if e:
                    error['phoneNumber'] = e

            # Check if error dict is empty
            if error:
                return ApiResponse(error=error, status=HTTPStatus.BAD_REQUEST)

            else:
                User.create(
                    username = username,
                    password = data['password'],
                    email = data['email'],
                    given_name = data['givenName'],
                    family_name = data['familyName'],
                    phone_number = data['phoneNumber']
                )
                return ApiResponse(message='Create success')


    def validate_username(self, username):
        if len(username) < 1:
            return 'Username cannot be empty'
        elif username == 'me':
            return '"me" cannot be your username'
        elif User.objects.filter(username=username).count() > 0:
            return 'Username has already been taken'
        return None

    def validate_password(self, password):
        if not re.match(r'^[A-Za-z0-9@#$%^&+=]{8,}$', password):
            return 'Password must have at least 8 characters and only contains A-Z,a-z,0-9,@,#,$,%,^,&,+,='
        return None

    def validate_email(self, email):
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return 'Invalid email format'
        return None

    def validate_given_name(self, given_name):
        if len(given_name) < 1:
            return 'Given name cannot be empty'
        return None

    def validate_family_name(self, family_name):
        if len(family_name) < 1:
            return 'Family name cannot be empty'
        return None

    def validate_phone_number(self, phone_number):
        if not re.match(r'^\d{8}$', phone_number):
            return 'Phone number must has 8 digit (HK phone number format)'
        return None



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

class UserWalletTransactionsView(View):

    http_method_names = ['get']

    def get(self, request, username, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)

        if username != 'me' and request.user.username != username:
            return ApiResponse(error_message='Cannot view other transactions', status=HTTPStatus.FORBIDDEN)

        try:
            user = request.user.user
        except User.DoesNotExist:
            return ApiResponse(error_message='Profile not found', status=HTTPStatus.INTERNAL_SERVER_ERROR)

        data = []

        for transaction in Transaction.objects.filter(
            Q(withdraw_wallet=user.wallet) | Q(deposit_wallet=user.wallet),
            time__gte = datetime.now(tz=timezone.utc) - timedelta(days=30)
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
class UserWalletView(View):

    http_method_names = ['get', 'put']

    def get(self, request, username, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)

        if username != 'me' and request.user.username != username:
            return ApiResponse(error_message='Cannot view other wallet', status=HTTPStatus.FORBIDDEN)

        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            return ApiResponse(error_message='Wallet not found', status=HTTPStatus.NOT_FOUND)

        data = dict(
            balance = wallet.balance
        )

        return ApiResponse(data=data)


    def put(self, request, username, *args, **kwargs):

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
                amount = changeAmount
            )
            return ApiResponse(message='deposit success')
        else:
            try:
                Transaction.create(
                    withdraw = user,
                    deposit = None,
                    amount = -changeAmount
                )
                return ApiResponse(message='withdraw success')
            except user.wallet.InsufficientBalanceError:
                return ApiResponse(error_message='Insufficient balance error', status=HTTPStatus.FORBIDDEN)
