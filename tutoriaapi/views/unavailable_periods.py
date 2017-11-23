from http import HTTPStatus

from django.contrib.auth.views import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from ..models import UnavailablePeriod

from .api_response import ApiResponse

class UnavailablePeriodView(View):

    http_method_names = ['get']

    def get(self, request, period_pk, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)
        
        try:
            # In the client point of view, a cancelled session has already been deleted,
            # so these cancelled session should not be displayed even if the client has explicitly
            # request the session with the right pk
            period = UnavailablePeriod.objects.get(pk=period_pk, cancelled=False)
        except UnavailablePeriod.DoesNotExist:
            return ApiResponse(error_message='Cannot find unavailable period with pk: {id}'.format(id=period_pk), status=HTTPStatus.NOT_FOUND)

        if request.user != period.tutor.user.base_user:
            return ApiResponse(error_message='Cannot view unavailable period which is not yours', status=HTTPStatus.FORBIDDEN)

        data = dict(
            pk = period.pk,
            startTime = period.start_time,
            endTime = period.end_time,
            cancellable = False # Stub
        )

        return ApiResponse(data=data)
    