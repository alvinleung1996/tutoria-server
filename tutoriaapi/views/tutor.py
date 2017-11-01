from datetime import timedelta
from decimal import Decimal
import json

from dateutil import parser

from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..models import Student, Tutor, CourseCode, Review, Tutorial

from .apiresponse import ApiResponse


class PlanningTutorialError(Exception):

    def __init__(self, message):
        super().__init__()
        self.message = message



def getPlanningTutorial(request, tutorUsername):
    startDate = parser.parse(request.GET.get('start-date', None))
    endDate = parser.parse(request.GET.get('end-date', None))
    if startDate is None or endDate is None:
        raise PlanningTutorialError('Invalid time')
    
    try:
        tutor = Tutor.objects.get(user__username=tutorUsername)
    except Tutor.DoesNotExist:
        raise PlanningTutorialError('Cannot find tutor')
    
    duration = endDate - startDate
    charge = tutor.hourlyRate * Decimal(duration / timedelta(hours=1))

    return dict(
        startDate = startDate,
        endDate = endDate,
        charge = charge
    )
    

class TutorialFeeView(View):

    http_method_names = ['get']

    def get(self, request, tutorUsername, *args, **kwargs):
        try:
            planningTutorial = getPlanningTutorial(request, tutorUsername)
        except PlanningTutorialError as e:
            return ApiResponse(error=dict(message=e.message))

        return ApiResponse(dict(charge=planningTutorial['charge']))



@method_decorator(csrf_exempt, name='dispatch')
class BookTutorialView(View):

    http_method_names = ['put']

    def put(self, request, tutorUsername, *args, **kwargs):

        if not request.user.is_authenticated:
            return ApiResponse(error=dict(message='Login required'))

        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return ApiResponse(error=dict(message='Does not have student role'))

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return ApiResponse(error=dict(message='Cannot recognize data'))

        try:
            tutor = Tutor.objects.get(user__username=tutorUsername)
        except Tutor.DoesNotExist:
            return ApiResponse(error=dict(message='Does not have tutor role'))

        if ('startDate' not in data) or ('endDate' not in data):
            return ApiResponse(error=dict(message='Data missing'))

        try:
            startDate = parser.parse(data['startDate'])
            endDate = parser.parse(data['endDate'])
        except (ValueError, OverflowError):
            return ApiResponse(error=dict(message='Wrong date format'))
        
        # TODO: Calc charge...

        tutorial = Tutorial.create(
            student = student,
            tutor = tutor,
            startDate = startDate,
            endDate = endDate
        )
        
        return ApiResponse(dict(tutorialId=tutorial.id))



class TutorProfileView(View):

    http_method_names = ['get']

    def get(self, request, tutorUsername, *args, **kwargs):

        try:
            tutor = Tutor.objects.get(user__username=tutorUsername)
        except Tutor.DoesNotExist:
            return ApiResponse(error=dict(message='Unknow tutor username'))

        tutorUser = tutor.user

        data = {
            'username': tutorUser.username,
            'givenName': tutorUser.givenName,
            'familyName': tutorUser.familyName,
            'avatar': tutorUser.avatar,
            'hourlyRate': tutor.hourlyRate,
            'university': tutor.university.name,
            'courseCodes': list(map(lambda c: c.code, tutor.courseCodeSet.all())),
            'subjectTags': list(map(lambda t: t.tag, tutor.subjectTagSet.all())),
            'averageReviewScore': tutor.averageReviewScore,
            'biography': tutor.biography,
            'reviews': [],
            'events': []
        }

        for entry in Review.objects.filter(tutorial__tutor=tutor):
            review = {
                'score': entry.score,
                'creationDate': entry.creationDate.isoformat(timespec='microseconds'),
                'comment': entry.comment
            }
            if not entry.anonymous:
                review['student'] = {
                    'givenName': entry.tutorial.student.user.givenName,
                    'familyName': entry.tutorial.student.user.familyName
                }
            data['reviews'].append(review)
        
        for entry in tutorUser.eventSet.filter(cancelled=False):
            event = {
                'startDate': entry.startDate.isoformat(timespec='microseconds'),
                'endDate': entry.endDate.isoformat(timespec='microseconds')
            }
            data['events'].append(event)

        return ApiResponse(data)
