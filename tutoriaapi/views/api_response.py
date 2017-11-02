from django.http import JsonResponse

class ApiResponse(JsonResponse):

    def __init__(self, data=None, *args, message=None, **kwargs):
        if message is not None:
            if data is None:
                data = {}
            data['message'] = message
        
        if 'status' in kwargs and isinstance(kwargs['status'], tuple):
            httpStatus = kwargs['status']
            kwargs['status'] = httpStatus[0]
            kwargs.setdefault('reason', httpStatus[1])
            
        super().__init__(data, *args, **kwargs)
        