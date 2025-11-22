import time
from typing import List

from exls.config import ConfigWorkspaceCreationPolling
from exls.shared.adapters.decorators import handle_service_errors
from exls.shared.core.service import ServiceError
from exls.workspaces.core.domain import DeployWorkspaceRequest, Workspace
from exls.workspaces.core.ports import IWorkspacesGateway


class WorkspacesService:
    def __init__(
        self,
        workspace_creation_polling_config: ConfigWorkspaceCreationPolling,
        workspaces_gateway: IWorkspacesGateway,
    ):
        self.workspace_creation_polling_config: ConfigWorkspaceCreationPolling = (
            workspace_creation_polling_config
        )
        self.workspaces_gateway: IWorkspacesGateway = workspaces_gateway

    @handle_service_errors("listing workspaces")
    def list_workspaces(self, cluster_id: str) -> List[Workspace]:
        return self.workspaces_gateway.list(cluster_id=cluster_id)

    @handle_service_errors("getting workspace")
    def get_workspace(self, workspace_id: str) -> Workspace:
        return self.workspaces_gateway.get(workspace_id=workspace_id)

    @handle_service_errors("deleting workspace")
    def delete_workspace(self, workspace_id: str) -> None:
        self.workspaces_gateway.delete(workspace_id=workspace_id)

    @handle_service_errors("deploying workspace")
    def deploy_workspace(self, request: DeployWorkspaceRequest) -> str:
        return self.workspaces_gateway.deploy(request=request)

    @handle_service_errors("polling workspace creation")
    def poll_workspace_creation(self, workspace_id: str) -> str:
        timeout = self.workspace_creation_polling_config.timeout_seconds
        polling_interval = (
            self.workspace_creation_polling_config.polling_interval_seconds
        )
        start_time = time.time()

        while time.time() - start_time < timeout:
            workspace: Workspace = self.get_workspace(workspace_id=workspace_id)
            if workspace.status == "RUNNING":
                return workspace_id
            if workspace.status == "FAILED":
                raise ServiceError(
                    f"workspace {workspace.name} ({workspace_id}) creation failed. "
                    + f"Status of workspace: {workspace.status}"
                ) from None

            time.sleep(polling_interval)
        else:
            raise ServiceError(
                f"workspace {workspace_id} did not become active in time."
            )
