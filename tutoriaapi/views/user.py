# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
from django.views import View

from ..models import User, Tutorial, UnavailablePeriod

from .apiresponse import ApiResponse

class UserEventsView(View):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return ApiResponse(error=dict(message='Login required'))

        user = request.user.user
        data = []
        for event in user.eventSet.filter(cancelled=False):
            concreteEvent = event.concreteEvent

            event = {
                'id': concreteEvent.id,
                'startDate': concreteEvent.startDate.isoformat(timespec='microseconds'),
                'endDate': concreteEvent.endDate.isoformat(timespec='microseconds')
            }

            if isinstance(concreteEvent, Tutorial):
                event['type'] = 'tutorial'
                event['student'] = {
                    'givenName': concreteEvent.student.user.givenName,
                    'familyName': concreteEvent.student.user.familyName
                }
                event['tutor'] = {
                    'givenName': concreteEvent.tutor.user.givenName,
                    'familyName': concreteEvent.tutor.user.familyName
                }

            elif isinstance(concreteEvent, UnavailablePeriod):
                event['type'] = 'unavailablePeriod'
                event['tutor'] = {
                    'givenName': concreteEvent.tutor.user.givenName,
                    'familyName': concreteEvent.tutor.user.familyName
                }
            
            data.append(event)

        return ApiResponse(data)
