import time
from typing import Dict, List

from exls.clusters.domain import Cluster
from exls.clusters.dtos import ClusterNodeDTO
from exls.clusters.gateway.base import ClustersGateway
from exls.clusters.service import ClustersService, get_clusters_service
from exls.config import AppConfig, ConfigWorkspaceCreationPolling
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.nodes.dtos import NodesListRequestDTO, NodeTypesDTO, SelfManagedNodeDTO
from exls.nodes.service import NodesService, get_node_service
from exls.workspaces.domain import Workspace
from exls.workspaces.dtos import (
    DeployWorkspaceRequestDTO,
    ListWorkspacesRequestDTO,
    WorkspaceDTO,
)
from exls.workspaces.gateway.base import WorkspacesGateway
from exls.workspaces.gateway.dtos import DeployWorkspaceParams
from exls.workspaces.mappers import (
    deploy_workspace_request_dto_to_deploy_workspace_params,
)


class WorkspacesService:
    def __init__(
        self,
        workspace_creation_polling_config: ConfigWorkspaceCreationPolling,
        workspaces_gateway: WorkspacesGateway,
        nodes_service: NodesService,
        clusters_gateway: ClustersGateway,
        clusters_service: ClustersService,
    ):
        self.workspace_creation_polling_config: ConfigWorkspaceCreationPolling = (
            workspace_creation_polling_config
        )
        self.workspaces_gateway: WorkspacesGateway = workspaces_gateway
        self.clusters_gateway: ClustersGateway = clusters_gateway
        # TODO: We should not use the clusters service here, but the clusters gateway
        self.clusters_service: ClustersService = clusters_service
        self.nodes_service: NodesService = nodes_service

    def _get_cluster_node_ip(self, cluster_id: str) -> str:
        cluster_nodes: List[ClusterNodeDTO] = self.clusters_service.get_cluster_nodes(
            cluster_id=cluster_id
        )

        nodes: List[SelfManagedNodeDTO] = self.nodes_service.list_nodes(
            NodesListRequestDTO(node_type=NodeTypesDTO.SELF_MANAGED)
        )
        nodes_by_id: Dict[str, SelfManagedNodeDTO] = {node.id: node for node in nodes}

        return nodes_by_id[cluster_nodes[0].node_id].endpoint

    @handle_service_errors("listing workspaces")
    def list_workspaces(self, request: ListWorkspacesRequestDTO) -> List[WorkspaceDTO]:
        cluster: Cluster = self.clusters_gateway.get(cluster_id=request.cluster_id)
        workspaces: List[Workspace] = self.workspaces_gateway.list(
            cluster_id=request.cluster_id
        )
        cluster_node_ip: str = self._get_cluster_node_ip(cluster_id=request.cluster_id)

        return [
            WorkspaceDTO.from_domain(
                workspace=workspace,
                cluster=cluster,
                cluster_node_ip=cluster_node_ip,
            )
            for workspace in workspaces
        ]

    @handle_service_errors("getting workspace")
    def get_workspace(self, workspace_id: str) -> WorkspaceDTO:
        workspace: Workspace = self.workspaces_gateway.get(workspace_id=workspace_id)
        cluster: Cluster = self.clusters_service.get_cluster(
            cluster_id=workspace.cluster_id
        )
        cluster_node_ip: str = self._get_cluster_node_ip(cluster_id=cluster.id)

        return WorkspaceDTO.from_domain(
            workspace=workspace,
            cluster=cluster,
            cluster_node_ip=cluster_node_ip,
        )

    @handle_service_errors("deleting workspace")
    def delete_workspace(self, workspace_id: str) -> None:
        self.workspaces_gateway.delete(workspace_id=workspace_id)

    @handle_service_errors("deploying workspace")
    def deploy_workspace(self, request: DeployWorkspaceRequestDTO) -> WorkspaceDTO:
        """
        Deploy a workspace using the deployment configuration.

        Args:
            config: Workspace deployment configuration from file or interactive flow

        Returns:
            WorkspaceDTO of the deployed workspace
        """
        deploy_params: DeployWorkspaceParams = (
            deploy_workspace_request_dto_to_deploy_workspace_params(request_dto=request)
        )
        workspace_id: str = self.workspaces_gateway.deploy(deploy_params=deploy_params)
        workspace: WorkspaceDTO = self.get_workspace(workspace_id=workspace_id)
        return workspace

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
    nodes_service: NodesService = get_node_service(
        config=config,
        access_token=access_token,
    )
    clusters_service: ClustersService = get_clusters_service(
        config=config,
        access_token=access_token,
    )

    return WorkspacesService(
        workspace_creation_polling_config=config.workspace_creation_polling,
        workspaces_gateway=workspaces_gateway,
        clusters_gateway=clusters_gateway,
        clusters_service=clusters_service,
        nodes_service=nodes_service,
    )
