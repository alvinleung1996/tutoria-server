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

        student_user = student.user

        data = dict(
            username = student_user.username,
            givenName = student_user.given_name,
            familyName = student_user.family_name,
            fullName = student_user.full_name,
            avatar = student_user.avatar,

            type = 'contracted' if student.type == Student.TYPE_CONTRACTED else 'privated',
            hourlyRate = student.hourly_rate,
            university = student.university.name,
            courseCodes = [c.code for c in student.course_code_set.all()],
            subjectTags = [t.tag for t in student.subject_tag_set.all()],
            averageReviewScore = -1,
            biography = student.biography,
            activated = student.activated,

            reviews = [],

            events = []
        )


        # TODO separate the following logic to another view

        if Studential.objects.filter(
            end_time__gt = datetime.now(tz=djtimezone.get_default_timezone()),
            student__user = request.user,
            student = student,
            cancelled = False
        ).count() > 0:
            data['phoneNumber'] = student_user.phone_number


        for review in Review.objects.filter(studential__student=student):
            item = dict(
                score = review.score,
                time = review.time.isoformat(timespec='microseconds'),
                comment = review.comment
            )
            if not review.anonymous:
                item['student'] = dict(
                    givenName = review.studential.student.user.given_name,
                    familyName = review.studential.student.user.family_name,
                    fullName = review.studential.student.user.full_name,
                    avatar = review.studential.student.user.avatar
                )
            data['reviews'].append(item)


        if len(data['reviews']) >= 3:
            data['averageReviewScore'] = student.average_review_score


        for event in student_user.event_set.filter(
            cancelled = False,
            end_time__gt = get_time(hour=0, minute=0)
        ):
            item = dict(
                startTime = event.start_time.isoformat(timespec='microseconds'),
                endTime = event.end_time.isoformat(timespec='microseconds')
            )
            data['events'].append(item)


        return ApiResponse(data)

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
