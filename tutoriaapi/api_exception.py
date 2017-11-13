class ApiException(Exception):

    def __init__(self, message=None, *args):
        self.message = message
        super().__init__(*(args if message is None else ((message,) + args)))
