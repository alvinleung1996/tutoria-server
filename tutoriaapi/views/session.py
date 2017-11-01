from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..models import Tutor, Event, Tutorial, UnavailablePeriod

from .apiresponse import ApiResponse


@method_decorator(csrf_exempt, name='dispatch')
class CancelEventView(View):
    
    http_method_names = ['delete']

    def delete(self, request, eventId, *args, **kwargs):

        if not request.user.is_authenticated:
            return ApiResponse(error=dict(message='Authenticated require!'))
        
        try:
            event = Event.objects.get(id=eventId)
        except Event.DoesNotExist:
            return ApiResponse(error=dict(message='Cannot find event with id: {id}'.format(id=eventId)))
        
        concreteEvent = event.concreteEvent

        if isinstance(concreteEvent, Tutorial):
            if concreteEvent.student.user.username != request.user.username:
                return ApiResponse(error=dict(messasge='Request denied'))
        
        elif isinstance(concreteEvent, UnavailablePeriod):
            if concreteEvent.tutor.user.username != request.user.username:
                return ApiResponse(error=dict(messasge='Request denied'))
        
        if concreteEvent.cancelled:
            return ApiResponse(dict(message='Event has already been cancelled'))
        
        concreteEvent.cancelled = True
        concreteEvent.save()
        
        return ApiResponse(dict(message='Success'))
