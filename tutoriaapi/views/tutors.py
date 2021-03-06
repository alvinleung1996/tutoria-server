from http import HTTPStatus
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone, timedelta
import json

from dateutil import parser

from django.contrib.auth.views import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils import timezone as djtimezone

from ..models import User, Tutor, CourseCode, Review, Event, Tutorial, University, UnavailablePeriod

from .api_response import ApiResponse
from ..api_exception import ApiException
from ..utils import get_time

class TutorSetSearchView(View):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)

        tutors = Tutor.objects.filter(activated=True).exclude(user=request.user)

        if 'given-name' in request.GET:
            tutors = tutors.filter(user__first_name__icontains=request.GET['given-name'])

        if 'family-name' in request.GET:
            tutors = tutors.filter(user__last_name__icontains=request.GET['family-name'])

        if 'university' in request.GET:
            tutors = tutors.filter(university__name__icontains=request.GET['university'])

        if 'type' in request.GET:
            if request.GET['type'] == 'contracted':
                tutors = tutors.filter(type=Tutor.TYPE_CONTRACTED)
            elif request.GET['type'] == 'private':
                tutors = tutors.filter(type=Tutor.TYPE_PRIVATE)

        if 'hourly-rate-min' in request.GET:
            tutors = tutors.filter(hourly_rate__gte=Decimal(request.GET['hourly-rate-min']))

        if 'hourly-rate-max' in request.GET:
            tutors = tutors.filter(hourly_rate__lte=Decimal(request.GET['hourly-rate-max']))

        if 'course-code' in request.GET:
            tutors = tutors.filter(course_code_set__code__icontains=request.GET['course-code'])

        if 'subject-tags' in request.GET:
            tutors = tutors.filter(subject_tag__tag__icontains=request.GET['subject-tags'])

        if 'free-only' in request.GET:
            free_only = bool(request.GET['free-only'])
        else:
            free_only = False

        data = []

        for tutor in tutors:
            user = tutor.user

            satisfy = True

            if free_only:

                is_free = False

                time_lower_bound = datetime.now(tz=timezone.utc)
                time_upper_bound = get_time(hour=0, minute=0, day_offset=7)

                events = Event.objects.filter(
                    user_set = tutor.user,
                    start_time__lt = time_upper_bound,
                    end_time__gt = time_lower_bound
                ).order_by('start_time', 'end_time')

                for event in events:
                    if event.start_time > time_lower_bound:
                        is_free = True
                        break
                    else:
                        time_lower_bound = max(time_lower_bound, event.end_time)

                if not is_free:
                    is_free = time_lower_bound < time_upper_bound

                satisfy = satisfy and is_free


            if satisfy:

                item = dict(
                    username = user.username,
                    givenName = user.given_name,
                    familyName = user.family_name,
                    fullName = user.full_name,
                    avatar = user.avatar,
                    hourlyRate = tutor.hourly_rate,
                    university = tutor.university.name,
                    courseCodes = [c.code for c in tutor.course_code_set.all()],
                    subjectTags = [t.tag for t in tutor.subject_tag_set.all()],
                    averageReviewScore = -1
                )

                if Review.objects.filter(tutorial__tutor=tutor).count() >= 3:
                    item['averageReviewScore'] = tutor.average_review_score

                data.append(item)

        if 'ordered-by' in request.GET:
            reverse = 'order' in request.GET and request.GET['order'] == 'descending'

            if request.GET['ordered-by'] == 'hourly-rate':
                data.sort(key=lambda i: i['hourlyRate'], reverse=reverse)
            elif request.GET['ordered-by'] == 'average-review-score':
                data.sort(key=lambda i: i['averageReviewScore'], reverse=reverse)

        return ApiResponse(data=data)


@method_decorator(csrf_exempt, name='dispatch')
class TutorView(View):

    http_method_names = ['get', 'put']

    def get(self, request, tutor_username, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)

        try:
            asking_user = request.user.user
        except User.DoesNotExist:
            return ApiResponse(error_message='User profile not found', status=HTTPStatus.INTERNAL_SERVER_ERROR)

        try:
            tutor = Tutor.objects.get(
                user__username = tutor_username if tutor_username != 'me' else request.user.username
            )
        except Tutor.DoesNotExist:
            return ApiResponse(error_message='Profile not found', status=HTTPStatus.NOT_FOUND)

        if asking_user != tutor.user and not tutor.activated:
            return ApiResponse(error_message='Tutor not activated', status=HTTPStatus.FORBIDDEN)

        tutor_user = tutor.user

        data = dict(
            username = tutor_user.username,
            givenName = tutor_user.given_name,
            familyName = tutor_user.family_name,
            fullName = tutor_user.full_name,
            avatar = tutor_user.avatar,

            type = 'contracted' if tutor.type == Tutor.TYPE_CONTRACTED else 'private',
            hourlyRate = tutor.hourly_rate,
            university = tutor.university.name,
            courseCodes = [c.code for c in tutor.course_code_set.all()],
            subjectTags = [t.tag for t in tutor.subject_tag_set.all()],
            averageReviewScore = -1,
            biography = tutor.biography,
            activated = tutor.activated,

            reviews = [],

            events = []
        )


        # TODO separate the following logic to another view

        if Tutorial.objects.filter(
            end_time__gt = datetime.now(tz=djtimezone.get_default_timezone()),
            student__user = request.user,
            tutor = tutor,
            cancelled = False
        ).count() > 0:
            data['phoneNumber'] = tutor_user.phone_number


        for review in Review.objects.filter(tutorial__tutor=tutor):
            item = dict(
                anonymous = review.anonymous,
                score = review.score,
                time = review.time.isoformat(timespec='microseconds'),
                comment = review.comment
            )
            if not review.anonymous:
                item['student'] = dict(
                    givenName = review.tutorial.student.user.given_name,
                    familyName = review.tutorial.student.user.family_name,
                    fullName = review.tutorial.student.user.full_name,
                    avatar = review.tutorial.student.user.avatar
                )
            data['reviews'].append(item)


        if len(data['reviews']) >= 3:
            data['averageReviewScore'] = tutor.average_review_score

        # Filter all event which is belonged to student or tutor
        # so that user can quickly check whether he is free at that time
        # TODO it is better to separate this to another request view,
        # it still here just for compatibility
        for event in Event.objects.filter(
            user_set__in = [tutor_user, asking_user],
            end_time__gt = get_time(hour=0, minute=0),
            cancelled = False
        ):
            item = dict(
                startTime = event.start_time.isoformat(timespec='microseconds'),
                endTime = event.end_time.isoformat(timespec='microseconds')
            )
            data['events'].append(item)


        return ApiResponse(data)


    def put(self, request, tutor_username, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)

        if tutor_username != 'me' and tutor_username != request.user.username:
            return ApiResponse(error_message='Cannot add/update tutor profile for other', status=HTTPStatus.FORBIDDEN)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return ApiResponse(error_message='Invalid body', status=HTTPStatus.BAD_REQUEST)

        try:
            tutor = Tutor.objects.get(user__username=request.user.username)
        except Tutor.DoesNotExist:
            tutor = None
        
        data = dict()
        error = dict()

        if tutor is not None:
            # Tutor want to update his/her tutor profile

            if 'type' in body:
                try:
                    data['type'] = self.validate_type(body['type'])
                except ApiException as e:
                    error['type'] = e.message

            if 'activated' in body:
                try:
                    data['activated'] = self.validate_activated(body['activated'])
                except ApiException as e:
                    error['activated'] = e.message

            if 'subjectTags' in body:
                try:
                    data['subject_tags'] = self.validate_subject_tags(body['subjectTags'])
                except ApiException as e:
                    error['subjectTags'] = e.message

            if 'university' in body:
                try:
                    data['university'] = self.validate_university(body['university'])
                except ApiException as e:
                    error['university'] = e.message

            if 'courseCodes' in body:
                try:
                    data['course_codes'] = self.validate_course_codes(body['courseCodes'])
                except ApiException as e:
                    error['courseCodes'] = e.message

            if 'hourlyRate' in body:
                try:
                    data['hourly_rate'] = self.validate_hourly_rate(body['hourlyRate'])
                except ApiException as e:
                    error['hourlyRate'] = e.message

            if 'biography' in body:
                try:
                    data['biography'] = self.validate_biography(body['biography'])
                except ApiException as e:
                    error['biography'] = e.message

            if error:
                return ApiResponse(error=error, status=HTTPStatus.BAD_REQUEST)
            
            # TODO fix potential key error: when user do not supply these 2 values
            if data['hourly_rate'] > Decimal('0') and data['type'] == Tutor.TYPE_CONTRACTED:
                return ApiResponse(error=dict(
                    hourlyRate = 'You cannot have a non zero hourly rate when you are a contact tutor',
                    type = 'You cannot be a contract tutor if you have a non zero hourly rate'
                ), status=HTTPStatus.BAD_REQUEST)

            if 'type' in data:
                tutor.type = data['type']

            if 'activated' in data:
                tutor.activated = data['activated']

            if 'subject_tags' in data:
                tutor.set_subject_tags(data['subject_tags'])

            if 'university' in data:
                tutor.university = data['university']

            if 'course_codes' in data:
                tutor.course_code_set.set(data['course_codes'])

            if 'hourly_rate' in data:
                tutor.hourly_rate = data['hourly_rate']

            if 'biography' in data:
                tutor.biography = data['biography']

            tutor.save()

            return ApiResponse(message='Update tutor profile success')

        else:
            # User want to create a new Tutor profile

            if 'type' not in body:
                error['type'] = 'Tutor type required'
            else:
                try:
                    data['type'] = self.validate_type(body['type'])
                except ApiException as e:
                    error['type'] = e.message

            if 'activated' not in body:
                data['activated'] = True
            else:
                try:
                    data['activated'] = self.validate_activated(body['activated'])
                except ApiException as e:
                    error['activated'] = e.message

            if 'subjectTags' not in body:
                data['subject_tags'] = []
            else:
                try:
                    data['subject_tags'] = self.validate_subject_tags(body['subjectTags'])
                except ApiException as e:
                    error['subjectTags'] = e.message

            if 'university' not in body:
                error['university'] = 'University required'
            else:
                try:
                    data['university'] = self.validate_university(body['university'])
                except ApiException as e:
                    error['university'] = e.message

            if 'courseCodes' not in body:
                error['courseCodes'] = 'Course codes required'
            else:
                try:
                    data['course_codes'] = self.validate_course_codes(body['courseCodes'])
                except ApiException as e:
                    error['courseCodes'] = e.message
            
            if 'hourlyRate' not in body:
                error['hourlyRate'] = 'Hourly rate required'
            else:
                try:
                    data['hourly_rate'] = self.validate_hourly_rate(body['hourlyRate'])
                except ApiException as e:
                    error['hourlyRate'] = e.message
            
            if 'biography' not in body:
                data['biography'] = ''
            else:
                try:
                    data['biography'] = self.validate_biography(body['biography'])
                except ApiException as e:
                    error['biography'] = e.message

            # Check if error dict is empty
            if error:
                return ApiResponse(error=error, status=HTTPStatus.BAD_REQUEST)

            if data['hourly_rate'] > Decimal('0') and data['type'] == Tutor.TYPE_CONTRACTED:
                return ApiResponse(error=dict(
                    hourlyRate = 'You cannot have a non zero hourly rate when you are a contact tutor',
                    type = 'You cannot be a contract tutor if you have a non zero hourly rate'
                ), status=HTTPStatus.BAD_REQUEST)

            else:
                request.user.user.add_role(Tutor, **data)
                return ApiResponse(message='Add tutor profile success')


    def validate_type(self, tutor_type):
        if tutor_type != 'contracted' and tutor_type != 'private':
            raise ApiException(message='Invalid type')
        return Tutor.TYPE_CONTRACTED if tutor_type == 'contracted' else Tutor.TYPE_PRIVATE

    def validate_activated(self, activated):
        return bool(activated)

    def validate_subject_tags(self, subject_tags):
        if not isinstance(subject_tags, list):
            raise ApiException(message='Invalid subjectTags format')
        elif '' in subject_tags:
            raise ApiException(message='No subject tag can be empty')
        # remove duplication
        return list(set(subject_tags))

    def validate_university(self, university):
        try:
            u = University.objects.get(name__iexact=university)
        except University.DoesNotExist as e:
            raise ApiException(message='Invalid university name')
        return u

    def validate_course_codes(self, course_codes):
        if not isinstance(course_codes, list):
            raise ApiException(message='Invalid course codes format')
        else:
            # remove duplication
            course_codes = set(course_codes)
            course_code_instances = []
            for code in course_codes:
                try:
                    course_code_instances.append(CourseCode.objects.get(code__iexact=code))
                except CourseCode.DoesNotExist as e:
                    raise ApiException(message='Cannot find course code "'+code+'"')
            
            return course_code_instances

    def validate_hourly_rate(self, hourly_rate):
        try:
            value = Decimal(hourly_rate)
        except InvalidOperation:
            raise ApiException(message='Invalid hourlyRate format')
        if value < 0 or (value % 10) != 0:
            raise ApiException(message='hourly rate must be >= 0 and is a multiple of 10')
        return value

    def validate_biography(self, biography):
        return biography.strip()



@method_decorator(csrf_exempt, name='dispatch')
class TutorUnavailablePeriodSetView(View):

    http_method_names = ['post']

    def post(self, request, tutor_username, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)

        if tutor_username != 'me' and tutor_username != request.user.username:
            return ApiResponse(error_message='Cannot add unavailable period for other tutor', status=HTTPStatus.FORBIDDEN)

        try:
            tutor = Tutor.objects.get(user__base_user=request.user)
        except Tutor.DoesNotExist:
            return ApiResponse(error_message='Missing tutor role', status=HTTPStatus.FORBIDDEN)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return ApiResponse(error_message='Invalid body', status=HTTPStatus.BAD_REQUEST)
        
        data = dict()
        error = dict()

        try:
            data['start_time'] = self.extract_start_time(body)
        except ApiException as e:
            error['startTime'] = e.message
        
        try:
            data['end_time'] = self.extract_end_time(body)
        except ApiException as e:
            error['endTime'] = e.message

        if 'start_time' in data and 'end_time' in data and data['end_time'] <= data['start_time']:
            error['endTime'] = 'Invalid time range'

        try:
            data['preview'] = self.extract_preview(body)
        except ApiException as e:
            error['preview'] = e.message
        
        if error:
            return ApiResponse(error=error, status=HTTPStatus.BAD_REQUEST)

        if data['start_time'] < datetime.now(tz=timezone.utc):
            return ApiResponse(error=dict(startTime='Start time has passed'), status=HTTPStatus.FORBIDDEN)

        if data['end_time'] > datetime.now(tz=timezone.utc) + timedelta(days=7):
            return ApiResponse(error=dict(endTime='End time must be within 7 days'), status=HTTPStatus.FORBIDDEN)
        
        if Event.objects.filter(
            user_set = tutor.user,
            start_time__lt = data['end_time'],
            end_time__gt = data['start_time'],
            cancelled = False
        ).count() > 0:
            return ApiResponse(error = dict(
                startTime = 'The request time has conflict with other events',
                endTime = 'The request time has conflict with other event'
            ), status=HTTPStatus.FORBIDDEN)
        
        if data['preview']:
            reply = dict(
                creatable = True
            )
            return ApiResponse(data=reply)

        else:
            period = UnavailablePeriod.create(
                tutor = tutor,
                start_time = data['start_time'],
                end_time = data['end_time'],
                cancelled = False
            )
            return ApiResponse(data=dict(pk=period.pk), message='Unavailable period created successfully')

    
    def extract_start_time(self, body):
        if 'startTime' not in body:
            raise ApiException(message='Require start time')
        try:
            time = parser.parse(body['startTime'])
        except (ValueError, OverflowError):
            raise ApiException(message='Invalid start time format')
        return time
    
    def extract_end_time(self, body):
        if 'endTime' not in body:
            raise ApiException(message='Require end time')
        try:
            time = parser.parse(body['endTime'])
        except (ValueError, OverflowError):
            raise ApiException(message='Invalid end time format')
        return time

    def extract_preview(self, body):
        if 'preview' not in body:
            return False
        return bool(body['preview'])
