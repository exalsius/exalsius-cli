from exls.workspaces.core.ports.operations import WorkspaceOperations
from exls.workspaces.core.ports.repository import WorkspaceRepository


# The gateway acts as the adapter here since there is no
# complex adapter logic needed.
class WorkspacesGateway(WorkspaceRepository, WorkspaceOperations):
    pass
