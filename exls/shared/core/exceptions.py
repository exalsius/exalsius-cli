class ExalsiusError(Exception):
    """Base exception for all Exalsius errors."""


class ExalsiusWarning(Warning):
    """Base warning for all Exalsius warnings."""


class ServiceError(ExalsiusError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message: str = message


class ServiceWarning(ExalsiusWarning):
    def __init__(self, message: str):
        super().__init__(message)
        self.message: str = message
