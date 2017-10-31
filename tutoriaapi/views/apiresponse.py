from django.http import JsonResponse

class ApiResponse(JsonResponse):

    def __init__(self, data=None, error=None, *args, **kwargs):
        body = {}
        if data is not None:
            body['data'] = data
        if error is not None:
            body['error'] = error
        super().__init__(body, *args, **kwargs)
        