import time
from typing import List

from exls.clusters.domain import Cluster
from exls.clusters.gateway.base import ClustersGateway
from exls.config import AppConfig, ConfigWorkspaceCreationPolling
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.workspaces.common.deploy_dtos import WorkspaceDeployConfigDTO
from exls.workspaces.common.domain import Workspace
from exls.workspaces.common.dtos import (
    ListWorkspacesRequestDTO,
    WorkspaceDTO,
)
from exls.workspaces.common.gateway.base import WorkspacesGateway


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
        cluster: Cluster = self.clusters_gateway.get(cluster_id=request.cluster_id)
        workspaces: List[Workspace] = self.workspaces_gateway.list(
            cluster_id=request.cluster_id
        )
        return [
            WorkspaceDTO.from_domain(workspace=workspace, cluster=cluster)
            for workspace in workspaces
        ]

    @handle_service_errors("getting workspace")
    def get_workspace(self, workspace_id: str) -> WorkspaceDTO:
        workspace: Workspace = self.workspaces_gateway.get(workspace_id=workspace_id)
        cluster: Cluster = self.clusters_gateway.get(cluster_id=workspace.cluster_id)
        return WorkspaceDTO.from_domain(workspace=workspace, cluster=cluster)

    @handle_service_errors("deleting workspace")
    def delete_workspace(self, workspace_id: str) -> None:
        self.workspaces_gateway.delete(workspace_id=workspace_id)

    @handle_service_errors("deploying workspace")
    def deploy_workspace(self, config: WorkspaceDeployConfigDTO) -> str:
        """
        Deploy a workspace using the deployment configuration.

        Args:
            config: Workspace deployment configuration from file or interactive flow

        Returns:
            workspace_id of the deployed workspace
        """
        return self.workspaces_gateway.deploy(config)

    @handle_service_errors("polling workspace creation")
    def poll_workspace_creation(self, workspace_id: str) -> WorkspaceDTO:
        # TODO: This belongs into the gateway layer
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
    )
    workspaces_gateway: WorkspacesGateway = gateway_factory.create_workspaces_gateway(
        access_token=access_token
    )
    clusters_gateway: ClustersGateway = gateway_factory.create_clusters_gateway(
        access_token=access_token
    )
    return WorkspacesService(
        workspace_creation_polling_config=config.workspace_creation_polling,
        workspaces_gateway=workspaces_gateway,
        clusters_gateway=clusters_gateway,
    )
