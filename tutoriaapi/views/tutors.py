from django.views import View

from ..models import Tutor, CourseCode, Review

from .apiresponse import ApiResponse

class SearchTutorsView(View):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):

        tutors = []

        for entry in Tutor.objects.all():
            user = entry.user

            tutor = {
                'username': user.username,
                'givenName': user.givenName,
                'familyName': user.familyName,
                'avatar': user.avatar,
                'hourlyRate': entry.hourlyRate,
                'university': entry.university.name,
                'courseCodes': list(map(lambda c: c.code, entry.courseCodeSet.all())),
                'subjectTags': list(map(lambda t: t.tag, entry.subjectTagSet.all())),
                'averageReviewScore': -1
            }
            
            if Review.objects.filter(tutorial__tutor=entry).count() >= 3:
                tutor['averageReviewScore'] = entry.averageReviewScore
            
            tutors.append(tutor)

        return ApiResponse(tutors)
