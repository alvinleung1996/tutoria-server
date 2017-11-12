import json
from decimal import Decimal
from datetime import timedelta
from http import HTTPStatus

from dateutil import parser

from django.contrib.auth.views import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import HttpResponse

from ..models import Student, Tutor, Tutorial

from .api_response import ApiResponse


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
                isTimeValid = preview['is_time_valid'],

                tutorFee = str(preview['tutor_fee']),
                commissionFee = str(preview['commission_fee']),
                couponDiscount = str(preview['coupon_discount']),
                totalFee = str(preview['total_fee']),

                coupon = preview['coupon'].code if preview['is_coupon_valid'] else None,
                isCouponValid = preview['is_coupon_valid'],

                balance = str(preview['balance']),
                isPayable = preview['is_payable'],

                isCreatable = preview['is_creatable']
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

            return ApiResponse(data=dict(tutorialId=tutorial.id))



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
        