from django.views import View

from ..models import Tutor, CourseCode, Review

from .api_response import ApiResponse


class SearchView(View):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(message='Login required', status=403)

        data = []

        for tutor in Tutor.objects.all():
            user = tutor.user

            item = dict(
                username = user.username,
                givenName = user.given_name,
                familyName = user.family_name,
                avatar = user.avatar,
                hourlyRate = tutor.hourly_rate,
                university = tutor.university.name,
                courseCodes = list(map(lambda c: c.code, tutor.course_code_set.all())),
                subjectTags = list(map(lambda t: t.tag, tutor.subject_tag_set.all())),
                averageReviewScore = -1
            )
            
            if Review.objects.filter(tutorial__tutor=tutor).count() >= 3:
                tutor['averageReviewScore'] = tutor.average_review_score
            
            data.append(item)

        return ApiResponse(dict(data=data))


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

