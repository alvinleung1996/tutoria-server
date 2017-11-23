import json
from http import HTTPStatus

from django.contrib.auth.views import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from ..models import Message

from .api_response import ApiResponse
from ..api_exception import ApiException


@method_decorator(csrf_exempt, name='dispatch')
class MessageView(View):

    http_method_names = ['get', 'put']

    def get(self, request, message_pk, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)

        try:
            message = Message.objects.get(pk=message_pk)
        except Message.DoesNotExist:
            return ApiResponse(error_message='Message not found', status=HTTPStatus.NOT_FOUND)

        try:
            user = request.user.user
        except User.DoesNotExist:
            return ApiResponse(error_message='User profile not found', status=HTTPStatus.INTERNAL_SERVER_ERROR)
        
        if message.send_user != user and message.receive_user != user:
            return ApiResponse(error_message='You cannot read this message', status=HTTPStatus.FORBIDDEN)

        data = dict(
            pk = message.pk,
            title = message.title,
            content = message.content,
            time = message.time.isoformat(timespec='microseconds')
        )

        data['direction'] = 'in' if message.receive_user == user else 'out'

        if message.send_user is not None:
            data['sendUser'] = dict(
                fullName = message.send_user.full_name
            )
        
        if message.receive_user is not None:
            data['receiveUser'] = dict(
                fullName = message.receive_user.full_name
            )
            data['read'] = message.read

        return ApiResponse(data=data)


    def put(self, request, message_pk, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_active:
            return ApiResponse(error_message='Login required', status=HTTPStatus.UNAUTHORIZED)

        try:
            message = Message.objects.get(pk=message_pk)
        except Message.DoesNotExist:
            return ApiResponse(error_message='Message not found', status=HTTPStatus.NOT_FOUND)

        try:
            user = request.user.user
        except User.DoesNotExist:
            return ApiResponse(error_message='User profile not found', status=HTTPStatus.INTERNAL_SERVER_ERROR)
        
        if message.send_user != user and message.receive_user != user:
            return ApiResponse(error_message='You cannot update this message', status=HTTPStatus.FORBIDDEN)

        try:
            body = json.loads(request.body)
            if not isinstance(body, dict):
                raise ApiException(message='body should be a dict')
        except (json.JSONDecodeError, ApiException):
            return ApiResponse(error_message='Invalid data', status=HTTPStatus.BAD_REQUEST)

        data = dict()
        error = dict()

        if 'read' in body:
            try:
                data['read'] = self.validate_read(body['read'])
            except ApiException as e:
                error['read'] = e.message
        
        if error:
            return ApiResponse(error=error)

        if 'read' in data:
            message.read = data['read']
        
        message.save()

        return ApiResponse(message='Message update success')

    
    def validate_read(self, read):
        return bool(read)
