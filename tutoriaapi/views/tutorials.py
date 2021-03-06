import json
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from dateutil import parser

from django.contrib.auth.views import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import HttpResponse

from ..models import Student, Tutor, Tutorial, Review

from .api_response import ApiResponse
from ..api_exception import ApiException


@method_decorator(csrf_exempt, name='dispatch')
class TutorialSetView(View):

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return ApiResponse(error_message='Invalid body', status=HTTPStatus.BAD_REQUEST)
        if not isinstance(body, dict):
            return ApiResponse(error_message='Invalid body', status=HTTPStatus.BAD_REQUEST)

        if ('studentUsername' not in body
                or 'tutorUsername' not in body
                or 'startTime' not in body
                or 'endTime' not in body):
            return ApiResponse(error_message='Incomplete body', status=HTTPStatus.BAD_REQUEST)

        if body['studentUsername'] != 'me' and request.user.username != body['studentUsername']:
            return ApiResponse(error_message='Cannot pretend to be someone else :-)', status=HTTPStatus.FORBIDDEN)

        try:
            start_time = parser.parse(body['startTime'])
            end_time = parser.parse(body['endTime'])
        except (ValueError, OverflowError):
            return ApiResponse(error_message='Wrong time format', status=HTTPStatus.BAD_REQUEST)
        
        try:
            student = Student.objects.get(user__base_user=request.user)
        except Student.DoesNotExist:
            return ApiResponse(error_message='Require student role', status=HTTPStatus.FORBIDDEN)

        try:
            tutor = Tutor.objects.get(user__username=body['tutorUsername'])
        except Tutor.DoesNotExist:
            return ApiResponse(error_message='Does not have tutor role', status=HTTPStatus.FORBIDDEN)

        if not tutor.activated:
            return ApiResponse(error_message='Tutor is not activated', status=HTTPStatus.FORBIDDEN)

        if student.user == tutor.user:
            return ApiResponse(error_message='Student cannot book its own session', status=HTTPStatus.FORBIDDEN)

        if 'couponCode' in body:
            coupon_code = body['couponCode']
        else:
            coupon_code = None

        if 'preview' in body and bool(body['preview']):

            preview = Tutorial.preview(
                student = student,
                tutor = tutor,
                start_time = start_time,
                end_time = end_time,
                coupon = coupon_code
            )
            data = dict(
                studentUsername = preview['student'].user.username,
                tutorUsername = preview['tutor'].user.username,

                startTime = preview['start_time'].isoformat(timespec='microseconds'),
                endTime = preview['end_time'].isoformat(timespec='microseconds'),
                timeValid = preview['time_valid'],

                tutorFee = str(preview['tutor_fee']),
                commissionFee = str(preview['commission_fee']),
                couponDiscount = str(preview['coupon_discount']),
                totalFee = str(preview['total_fee']),

                # Deprecated
                coupon = preview['coupon'].code if preview['coupon_valid'] else None,
                # Use couponCode instead of coupon
                couponCode = preview['coupon'].code if preview['coupon_valid'] else None,
                couponValid = preview['coupon_valid'],

                balance = str(preview['balance']),
                isPayable = preview['is_payable'],

                creatable = preview['creatable']
            )
            return ApiResponse(data=data)
        
        else:
            try:
                tutorial = Tutorial.create(
                    student = student,
                    tutor = tutor,
                    start_time = start_time,
                    end_time = end_time,
                    coupon = coupon_code
                )
            except Tutorial.TutorialNotCreatableError:
                return ApiResponse(error_message='Invalid tutorial parameters', status=HTTPStatus.FORBIDDEN)
            
            data = dict(
                studentUsername = tutorial.student.user.username,
                tutorUsername = tutorial.tutor.user.username,

                startTime = tutorial.start_time.isoformat(timespec='microseconds'),
                endTime = tutorial.end_time.isoformat(timespec='microseconds'),

                tutorFee = str(tutorial.tutor_fee),
                commissionFee = str(tutorial.commission_fee),
                couponDiscount = str(tutorial.coupon_discount),
                totalFee = str(tutorial.total_fee),

                coupon = tutorial.coupon.code if tutorial.coupon is not None else None,

                balance = str(tutorial.student.user.wallet.balance)
            )
            return ApiResponse(data=data)



@method_decorator(csrf_exempt, name='dispatch')
class TutorialView(View):

    http_method_names = ['get', 'delete']

    def get(self, request, tutorial_id, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)
        
        try:
            tutorial = Tutorial.objects.get(id=tutorial_id)
        except Tutorial.DoesNotExist:
            return ApiResponse(error_message='Cannot find event with id: {id}'.format(id=tutorial_id), status=HTTPStatus.NOT_FOUND)

        if request.user.username != tutorial.student.user.username and request.user.username != tutorial.tutor.user.username:
            return ApiResponse(error_message='Cannot view tutorial which is not related to you', status=HTTPStatus.FORBIDDEN)
        
        reviewable = (not tutorial.cancelled
                      and tutorial.end_time <= datetime.now(tz=timezone.utc)
                      and not hasattr(tutorial, 'review'))

        data = dict(
            id = tutorial.id,

            startTime = tutorial.start_time,
            endTime = tutorial.end_time,

            cancelled = tutorial.cancelled,
            cancellable = tutorial.cancellable,

            student = dict(
                username = tutorial.student.user.username,
                fullName = tutorial.student.user.full_name,
                avatar = tutorial.student.user.avatar,
                phoneNumber = tutorial.student.user.phone_number
            ),
            tutor = dict(
                username = tutorial.tutor.user.username,
                fullName = tutorial.tutor.user.full_name,
                avatar = tutorial.tutor.user.avatar,
                phoneNumber = tutorial.tutor.user.phone_number
            ),

            totalFee = str(tutorial.total_fee),

            reviewable = reviewable

            # more field if needed!
        )
        return ApiResponse(data=data)
        
    
    def delete(self, request, tutorial_id, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)
        
        try:
            tutorial = Tutorial.objects.get(id=tutorial_id)
        except Tutorial.DoesNotExist:
            return ApiResponse(error_message='Cannot find event with id: {id}'.format(id=tutorial_id), status=HTTPStatus.NOT_FOUND)

        if request.user.username != tutorial.student.user.username:
            return ApiResponse(error_message='Cannot cancel tutorial which is not booked by you', status=HTTPStatus.FORBIDDEN)
        
        if tutorial.cancelled:
            return ApiResponse(message='Tutorial has already been cancelled')
        
        try:
            tutorial.cancel()
        except ApiException as e:
            return ApiResponse(error_message='Cannot cancel tutorial: '+e.message, status=HTTPStatus.FORBIDDEN)
        
        return ApiResponse(message='Success')

@method_decorator(csrf_exempt, name='dispatch')
class TutorialReviewView(View):

    http_method_names = ['put']

    def put(self, request, tutorial_id, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)
        
        try:
            tutorial = Tutorial.objects.get(id=tutorial_id)
        except Tutorial.DoesNotExist:
            return ApiResponse(error_message='Cannot find event with id: {id}'.format(id=tutorial_id), status=HTTPStatus.NOT_FOUND)

        if request.user.username != tutorial.student.user.username:
            return ApiResponse(error_message='Cannot review other\'s tutorial', status=HTTPStatus.FORBIDDEN)

        if tutorial.cancelled:
            return ApiResponse(error_message='Tutorial has been cancelled', status=HTTPStatus.FORBIDDEN)

        if tutorial.end_time > datetime.now(tz=timezone.utc):
            return ApiResponse(error_message='Tutorial has not been completed', status=HTTPStatus.FORBIDDEN)

        try:
            body = json.loads(request.body)
            if not isinstance(body, dict):
                raise ApiException(message='Body must be a JSON object')
        except json.JSONDecodeError:
            return ApiResponse(error_message='Invalid body format', status=HTTPStatus.BAD_REQUEST)
        
        if hasattr(tutorial, 'review'):
            return ApiResponse(error_message='Tutorial has already been reviewed', status=HTTPStatus.FORBIDDEN)

        data = dict()
        error = dict()

        if 'score' not in body:
            error['score'] = 'Score is required'
        else:
            try:
                data['score'] = self.validate_score(body['score'])
            except ApiException as e:
                error['score'] = e.message
        
        if 'anonymous' not in body:
            data['anonymous'] = False
        else:
            try:
                data['anonymous'] = self.validate_anonymous(body['anonymous'])
            except ApiException as e:
                error['anonymous'] = e.message
        
        if 'comment' not in body:
            data['comment'] = ''
        else:
            try:
                data['comment'] = self.validate_comment(body['comment'])
            except ApiException as e:
                error['comment'] = e.message

        if error:
            return ApiResponse(error=error, status=HTTPStatus.BAD_REQUEST)

        pk = Review.create(
            tutorial = tutorial,
            comment = data['comment'],
            score = data['score'],
            anonymous = data['anonymous']
        ).pk

        return ApiResponse(data=dict(pk=pk), message='Review success')

    
    def validate_score(self, score):
        try:
            value = int(score)
        except ValueError:
            raise ApiException(message='Score must be a number')
        if value < 0 or value > 5:
            raise ApiException(message='Score must be in the range [0, 5]')
        return value

    def validate_comment(self, comment):
        return comment.strip()
    
    def validate_anonymous(self, anonymous):
        return bool(anonymous)
