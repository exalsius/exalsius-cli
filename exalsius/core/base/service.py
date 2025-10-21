from exalsius.core.base.exceptions import ExalsiusError


class ServiceError(ExalsiusError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message: str = message
