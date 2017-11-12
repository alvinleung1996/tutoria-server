from django.http import JsonResponse

class ApiResponse(JsonResponse):

    def __init__(self, data=None, message=None, error=None, error_message=None, *args, **kwargs):
        """
        Args:
            data: dict
            message: str
            error: dict
            error_message: str
        """
        body = {}
        
        if data is not None:
            body['data'] = data
        
        if message is not None:
            if 'data' not in body:
                body['data'] = {}
            body['data']['message'] = message
        
        if error is not None:
            body['error'] = error
        
        if error_message is not None:
            if 'error' not in body:
                body['error'] = {}
            body['error']['message'] = error_message
        
        if 'status' in kwargs and isinstance(kwargs['status'], tuple):
            httpStatus = kwargs['status']
            kwargs['status'] = httpStatus[0]
            kwargs.setdefault('reason', httpStatus[1])
            
        super().__init__(body, *args, **kwargs)
        