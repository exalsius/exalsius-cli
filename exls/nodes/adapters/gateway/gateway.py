from exls.nodes.core.ports.operations import NodesOperations
from exls.nodes.core.ports.repository import NodesRepository


# The gateway acts as the adapter here since there is no
# complex adapter logic needed.
class NodesGateway(NodesRepository, NodesOperations):
    pass
