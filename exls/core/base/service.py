from exls.core.base.exceptions import ExalsiusError, ExalsiusWarning


class ServiceError(ExalsiusError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message: str = message


class ServiceWarning(ExalsiusWarning):
    def __init__(self, message: str):
        super().__init__(message)
        self.message: str = message
