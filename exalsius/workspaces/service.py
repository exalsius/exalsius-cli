import time
from typing import List

from exalsius.clusters.domain import Cluster
from exalsius.clusters.gateway.base import ClustersGateway
from exalsius.config import AppConfig, ConfigWorkspaceCreationPolling
from exalsius.core.commons.decorators import handle_service_errors
from exalsius.core.commons.factories import GatewayFactory
from exalsius.workspaces.domain import Workspace, WorkspaceFilterParams
from exalsius.workspaces.dtos import ListWorkspacesRequestDTO, WorkspaceDTO
from exalsius.workspaces.gateway.base import WorkspacesGateway


class WorkspacesService:
    def __init__(
        self,
        workspace_creation_polling_config: ConfigWorkspaceCreationPolling,
        workspaces_gateway: WorkspacesGateway,
        clusters_gateway: ClustersGateway,
    ):
        self.workspace_creation_polling_config: ConfigWorkspaceCreationPolling = (
            workspace_creation_polling_config
        )
        self.workspaces_gateway: WorkspacesGateway = workspaces_gateway
        self.clusters_gateway: ClustersGateway = clusters_gateway

    @handle_service_errors("listing workspaces")
    def list_workspaces(self, request: ListWorkspacesRequestDTO) -> List[WorkspaceDTO]:
        workspace_filter_params: WorkspaceFilterParams = WorkspaceFilterParams(
            cluster_id=request.cluster_id
        )
        workspaces: List[Workspace] = self.workspaces_gateway.list(
            workspace_filter_params=workspace_filter_params
        )

        cluster: Cluster = self.clusters_gateway.get(cluster_id=request.cluster_id)

        return [
            WorkspaceDTO.from_domain(workspace=w, cluster=cluster) for w in workspaces
        ]

    @handle_service_errors("getting workspace")
    def get_workspace(self, workspace_id: str) -> WorkspaceDTO:
        workspace: Workspace = self.workspaces_gateway.get(workspace_id=workspace_id)
        cluster: Cluster = self.clusters_gateway.get(cluster_id=workspace.cluster_id)
        return WorkspaceDTO.from_domain(workspace=workspace, cluster=cluster)

    @handle_service_errors("deleting workspace")
    def delete_workspace(self, workspace_id: str) -> None:
        self.workspaces_gateway.delete(workspace_id=workspace_id)

    @handle_service_errors("polling workspace creation")
    def poll_workspace_creation(self, workspace_id: str) -> WorkspaceDTO:
        timeout = self.workspace_creation_polling_config.timeout_seconds
        polling_interval = (
            self.workspace_creation_polling_config.polling_interval_seconds
        )
        start_time = time.time()

        while time.time() - start_time < timeout:
            workspace_dto: WorkspaceDTO = self.get_workspace(workspace_id=workspace_id)
            if workspace_dto.workspace_status == "RUNNING":
                return workspace_dto
            if workspace_dto.workspace_status == "FAILED":
                # Re-raising as a service error would be better but let's stick to the original logic for now
                raise Exception(
                    f"workspace {workspace_dto.workspace_name} ({workspace_id}) creation failed. "
                    + f"Status of workspace: {workspace_dto.workspace_status}"
                )

            time.sleep(polling_interval)
        else:
            raise TimeoutError(
                f"workspace {workspace_id} did not become active in time."
            )


def get_workspaces_service(config: AppConfig, access_token: str) -> WorkspacesService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
        access_token=access_token,
    )
    workspaces_gateway: WorkspacesGateway = gateway_factory.create_workspaces_gateway()
    clusters_gateway: ClustersGateway = gateway_factory.create_clusters_gateway()
    return WorkspacesService(
        workspace_creation_polling_config=config.workspace_creation_polling,
        workspaces_gateway=workspaces_gateway,
        clusters_gateway=clusters_gateway,
    )
