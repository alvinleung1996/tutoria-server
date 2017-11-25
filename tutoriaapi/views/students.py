from http import HTTPStatus
from decimal import Decimal, InvalidOperation
import json

from django.contrib.auth.views import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils import timezone as djtimezone

from ..models import Student

from .api_response import ApiResponse
from ..api_exception import ApiException



@method_decorator(csrf_exempt, name='dispatch')
class StudentView(View):

    http_method_names = ['get', 'put']

    def get(self, request, student_username, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)

        try:
            student = Student.objects.get(
                user__username = student_username if student_username != 'me' else request.user.username
            )
        except Student.DoesNotExist:
            return ApiResponse(error_message='Profile not found', status=HTTPStatus.NOT_FOUND)

        data = dict()

        return ApiResponse(data=data)

    def put(self, request, student_username, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)

        if student_username != 'me' and student_username != request.user.username:
            return ApiResponse(error_message='Cannot add/update student profile for other', status=HTTPStatus.FORBIDDEN)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return ApiResponse(error_message='Invalid body', status=HTTPStatus.BAD_REQUEST)

        try:
            student = Student.objects.get(user__base_user=request.user)
        except Student.DoesNotExist:
            student = None

        if student is not None:
            # Student want to update his/her student profile

            # Nothing can be updated...

            return ApiResponse(message='Update student profile success')

        else:
            # User want to create a new Student profile

            request.user.user.add_role(Student)
            return ApiResponse(message='Add student profile success')
