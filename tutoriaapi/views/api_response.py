from django.http import JsonResponse

class ApiResponse(JsonResponse):

    def __init__(self, *args, message=None, **kwargs):
        if message is not None:
            kwargs['content'] = dict(message=message)
        super().__init__(*args, **kwargs)
        