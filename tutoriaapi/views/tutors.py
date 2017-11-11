from django.views import View

from ..models import Tutor, CourseCode, Review

from .api_response import ApiResponse


class SearchView(View):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(message='Login required', status=403)

        need_filter_for_coursecode = False
        need_filter_for_subject_tag = False
        order = request.GET['order_by']
        given_name = request.GET['given_name']
        family_name = request.GET['family_name']
        university = request.GET['university']
        type = request.GET['type']
        upper_bound = request.GET['upper_bound']
        lower_bound = request.GET['lower_bound']
        coursecode = request.GET['coursecode']
        subject_tag = request.GET['subject_tag']
        available_in_the_next_seven_days = request.GET['extra']


        results = Tutor.objects.all()
        results = results.filter(activated=True).order_by('hourlyRate')

        if order != '':
            results = results.order_by(order)

        if given_name != '':
            results = results.filter(user__given_name=given_name)

        if family_name != '':
            results = results.filter(user__family_name=family_name)

        if university != '':
            results = results.filter(university__name=university)

        if type != '':
            results = results.filter(type=type)

        if upper_bound != '':
            results = results.filter(hourly_rate__lte=upper_bound)

        if lower_bound != '':
            results = results.filter(hourly_rate__gte=lower_bound)

        if coursecode != '':
            need_filter_for_coursecode = True

        if subject_tag != '':
            need_filter_for_subject_tag = True


        data = []

        for tutor in results:
            user = tutor.user

            satisfy = True

            subject_tags = list(map(lambda t: t.tag, tutor.subjectTagSet.all()))
            course_codes = list(map(lambda c: c.code, tutor.courseCodeSet.all()))

            if need_filter_for_coursecode == True:
                if coursecode not in course_codes:
                    satisfy = False

            if need_filter_for_subject_tag == True:
                if subject_tag not in subject_tags:
                    satisfy = False

            if satisfy == True:
                item = dict{
                    'username': user.username,
                    'givenName': user.given_name,
                    'familyName': user.family_name,
                    'avatar': user.avatar,
                    'hourlyRate': tutor.hourly_rate,
                    'university': tutor.university.name,
                    'courseCodes': course_codes,
                    'subjectTags': subject_tags,
                    'averageReview_score': -1
                }
            
                if Review.objects.filter(tutorial__tutor=tutor).count() >= 3:
                    tutor['averageReviewScore'] = tutor.averageReviewScore
            
                data.append(tutor)

        return ApiResponse(data)


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

