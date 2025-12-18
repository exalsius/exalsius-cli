from exls.services.core.ports.operations import ServiceOperations
from exls.services.core.ports.repository import ServiceRepository


# The gateway acts as the adapter here since there is no
# complex adapter logic needed.
class ServicesGateway(ServiceRepository, ServiceOperations):
    pass
