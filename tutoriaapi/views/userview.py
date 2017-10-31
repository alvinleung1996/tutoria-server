# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.contrib.auth.models import User

from ..models import UserProfile, TutorialSession, BlackenOutSession

from .apiresponse import ApiResponse

# @method_decorator(csrf_exempt, name='dispatch')
class UserSessionsView(View):

    http_method_names = ['get']

    def get(self, request, username, *args, **kwargs):

        if not request.user.is_authenticated:
            return ApiResponse(error=dict(message='Login required'))
        
        if username is not None and request.user.username != username:
            return ApiResponse(error=dict(message='Cannot access other sessions'))

        profile = request.user.userProfile if username is None else User.objects.get(username=username).userProfile
        sessions = profile.occupiedSessions
        data = []
        for session in sessions:
            concreteSession = session.concreteSession

            event = {
                'startDate': concreteSession.startDate.isoformat(timespec='microseconds'),
                'endDate': concreteSession.endDate.isoformat(timespec='microseconds')
            }

            if isinstance(concreteSession, TutorialSession):
                event['type'] = 'tutorial'
                event['student'] = {
                    'givenName': concreteSession.studentRole.userProfile.givenName,
                    'familyName': concreteSession.studentRole.userProfile.familyName
                }
                event['tutor'] = {
                    'givenName': concreteSession.tutorRole.userProfile.givenName,
                    'familyName': concreteSession.tutorRole.userProfile.familyName
                }
            elif isinstance(concreteSession, BlackenOutSession):
                event['type'] = 'blackenOut'
            
            data.append(event)

        return ApiResponse(data)
