from http import HTTPStatus
from decimal import Decimal

from django.views import View

from ..models import Tutor, CourseCode, Review, Event

from .api_response import ApiResponse
from ..utils import get_time

class SearchView(View):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED) 

        tutors = Tutor.objects.filter(activated=True).exclude(user__base_user=request.user)

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
            tutors = tutors.filter(subject_tag_set__tag__icontains=request.GET['subject-tags'])

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

                time_lower_bound = get_time(hour=0, minute=0)
                time_upper_bound = get_time(hour=0, minute=0, day_offset=7)

                events = Event.objects.filter(
                    user_set__tutor = tutor,
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


class ProfileView(View):

    http_method_names = ['get']

    def get(self, request, tutor_username, *args, **kwargs):

        try:
            tutor = Tutor.objects.get(user__username=tutor_username)
        except Tutor.DoesNotExist:
            return ApiResponse(message='Profile not found', status=404)

        tutor_user = tutor.user

        data = dict(
            username = tutor_user.username,
            givenName = tutor_user.given_name,
            familyName = tutor_user.family_name,
            avatar = tutor_user.avatar,
            hourlyRate = tutor.hourly_rate,
            university = tutor.university.name,
            courseCodes = list(map(lambda c: c.code, tutor.course_code_set.all())),
            subjectTags = list(map(lambda t: t.tag, tutor.subject_tag_set.all())),
            averageReviewScore = tutor.average_review_score,
            biography = tutor.biography,
            reviews = [],
            events = []
        )

        for review in Review.objects.filter(tutorial__tutor=tutor):
            item = dict(
                score = review.score,
                time = review.time.isoformat(timespec='microseconds'),
                comment = entry.comment
            )
            if not review.anonymous:
                item['student'] = dict(
                    givenName = entry.tutorial.student.user.given_name,
                    familyName = entry.tutorial.student.user.family_name
                )
            data['reviews'].append(item)
        
        for event in tutor_user.event_set.filter(cancelled=False):
            item = dict(
                startTime = event.start_time.isoformat(timespec='microseconds'),
                endTime = event.end_time.isoformat(timespec='microseconds')
            )
            data['events'].append(item)

        return ApiResponse(data)

