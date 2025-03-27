class ExalsiusError(Exception):
    """Base exception for all Exalsius errors"""

    pass


class ColonyOperationError(ExalsiusError):
    """Raised when colony operations fail"""

    pass


class KubernetesClientError(ExalsiusError):
    """Raised when Kubernetes operations fail"""

    pass


class CloudOperationError(ExalsiusError):
    """Raised when cloud operations fail"""

    pass
