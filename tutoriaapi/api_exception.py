class ApiException(Exception):

    def __init__(self, error=None, message=None, *args):
        self.error = error
        self.message = message
        super().__init__(*(args if message is None else ((message,) + args)))
