class ApiException(Exception):

    def __init__(self, message=None, *args):
        super().__init__(*(args if message is None else (message + args)))
