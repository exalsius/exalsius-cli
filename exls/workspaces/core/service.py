from typing import List

from pydantic.types import PositiveFloat

from exls.config import ConfigWorkspaceCreationPolling
from exls.shared.adapters.decorators import handle_service_layer_errors
from exls.shared.core.polling import poll_until
from exls.shared.core.service import ServiceError
from exls.workspaces.core.domain import (
    AvailableClusterResources,
    Workspace,
    WorkspaceCluster,
    WorkspaceClusterStatus,
    WorkspaceStatus,
    WorkspaceTemplate,
)
from exls.workspaces.core.ports.gateway import (
    DeployWorkspaceParameters,
    IWorkspacesGateway,
    deploy_workspace_request_to_deploy_parameters,
)
from exls.workspaces.core.ports.provider import (
    IClustersProvider,
    IWorkspaceTemplatesProvider,
)
from exls.workspaces.core.requests import (
    AssignedMultiNodeWorkspaceResources,
    AssignedSingleNodeWorkspaceResources,
    DeployWorkspaceRequest,
)


class WorkspacesService:
    def __init__(
        self,
        workspace_creation_polling_config: ConfigWorkspaceCreationPolling,
        workspaces_gateway: IWorkspacesGateway,
        clusters_provider: IClustersProvider,
        workspace_templates_provider: IWorkspaceTemplatesProvider,
    ):
        self._workspace_creation_polling_config: ConfigWorkspaceCreationPolling = (
            workspace_creation_polling_config
        )
        self._workspaces_gateway: IWorkspacesGateway = workspaces_gateway
        self._clusters_provider: IClustersProvider = clusters_provider
        self._workspace_templates_provider: IWorkspaceTemplatesProvider = (
            workspace_templates_provider
        )

    def _get_and_validate_cluster(self, cluster_id: str) -> WorkspaceCluster:
        cluster: WorkspaceCluster = self._clusters_provider.get_cluster(
            cluster_id=cluster_id
        )
        if cluster.status != WorkspaceClusterStatus.READY:
            raise ServiceError(
                f"Cluster {cluster.name} ({cluster_id}) is not ready. Current status: {cluster.status}"
            )
        return cluster

    @handle_service_layer_errors("listing workspaces")
    def list_workspaces(self, cluster_id: str) -> List[Workspace]:
        self._get_and_validate_cluster(cluster_id=cluster_id)
        return self._workspaces_gateway.list(cluster_id=cluster_id)

    @handle_service_layer_errors("getting workspace")
    def get_workspace(self, workspace_id: str) -> Workspace:
        return self._workspaces_gateway.get(workspace_id=workspace_id)

    @handle_service_layer_errors("deleting workspace")
    def delete_workspace(self, workspace_id: str) -> None:
        self._workspaces_gateway.delete(workspace_id=workspace_id)

    def _wait_for_workspace_status(
        self, workspace_id: str, target_status: WorkspaceStatus
    ) -> Workspace:
        return poll_until(
            fetcher=lambda: self.get_workspace(workspace_id=workspace_id),
            predicate=lambda workspace: workspace.status == target_status,
            timeout_seconds=self._workspace_creation_polling_config.timeout_seconds,
            interval_seconds=self._workspace_creation_polling_config.polling_interval_seconds,
        )

    @handle_service_layer_errors("deploying workspace")
    def deploy_workspace(
        self, request: DeployWorkspaceRequest, wait_for_ready: bool = False
    ) -> Workspace:
        self._get_and_validate_cluster(cluster_id=request.cluster_id)

        # TODO: Validate request
        # - check if workspace name is unique
        # - check if resources are available on the cluster

        deploy_parameters: DeployWorkspaceParameters = (
            deploy_workspace_request_to_deploy_parameters(
                request=request,
            )
        )

        workspace_id: str = self._workspaces_gateway.deploy(
            parameters=deploy_parameters
        )

        workspace: Workspace
        if wait_for_ready:
            workspace = self._wait_for_workspace_status(
                workspace_id=workspace_id, target_status=WorkspaceStatus.RUNNING
            )
        else:
            workspace = self.get_workspace(workspace_id=workspace_id)

        return workspace

    @handle_service_layer_errors("getting cluster")
    def get_cluster(self, cluster_id: str) -> WorkspaceCluster:
        return self._clusters_provider.get_cluster(cluster_id=cluster_id)

    @handle_service_layer_errors("listing workspace templates")
    def get_workspace_templates(self) -> List[WorkspaceTemplate]:
        return self._workspace_templates_provider.list_workspace_templates()

    @handle_service_layer_errors("listing clusters")
    def list_clusters(self) -> List[WorkspaceCluster]:
        return self._clusters_provider.list_clusters()

    @handle_service_layer_errors("getting resources for workspace")
    def get_resources_for_single_node_workspace(
        self, cluster_id: str, num_gpus: int
    ) -> AssignedSingleNodeWorkspaceResources:
        cluster: WorkspaceCluster = self._get_and_validate_cluster(
            cluster_id=cluster_id
        )
        available_cluster_resources: List[AvailableClusterResources] = (
            self._clusters_provider.get_cluster_resources(cluster_id=cluster_id)
        )

        for resource in available_cluster_resources:
            if resource.gpu_count >= num_gpus:
                return AssignedSingleNodeWorkspaceResources(
                    gpu_count=num_gpus,
                    gpu_type=resource.gpu_type,
                    gpu_vendor=resource.gpu_vendor,
                    cpu_cores=int((resource.cpu_cores / resource.gpu_count) * num_gpus),
                    memory_gb=int((resource.memory_gb / resource.gpu_count) * num_gpus),
                    storage_gb=int(
                        (resource.storage_gb / resource.gpu_count) * num_gpus
                    ),
                )
        raise ServiceError(
            f"Cluster {cluster.name} ({cluster_id}) does not have a node with at least {num_gpus} requested "
            f"GPU{'' if num_gpus == 1 else 's'}."
        )

    @handle_service_layer_errors("getting resources for distributed training workspace")
    def get_resources_for_multi_node_workspace(
        self, cluster_id: str, resource_split_tolerance: PositiveFloat = 0.1
    ) -> AssignedMultiNodeWorkspaceResources:
        cluster: WorkspaceCluster = self._get_and_validate_cluster(
            cluster_id=cluster_id
        )
        available_cluster_resources: List[AvailableClusterResources] = (
            self._clusters_provider.get_cluster_resources(cluster_id=cluster_id)
        )

        total_nodes: int = sum(
            [resource.gpu_count for resource in available_cluster_resources]
        )
        if total_nodes < 2:
            raise ServiceError(
                (
                    f"Cluster {cluster.name} ({cluster_id}) does not have enough "
                    "available GPUs to deploy a distributed training workspace. "
                    f"Needs at least 2 GPUs. Has {total_nodes} GPUs."
                )
            )

        cpu_split: int = min(
            [
                int(resource.cpu_cores / resource.gpu_count)
                for resource in available_cluster_resources
            ]
        )
        memory_split: int = min(
            [
                int(resource.memory_gb / resource.gpu_count)
                for resource in available_cluster_resources
            ]
        )
        storage_split: int = min(
            [
                int(resource.storage_gb / resource.gpu_count)
                for resource in available_cluster_resources
            ]
        )

        if resource_split_tolerance > 0:
            cpu_split = int(cpu_split * (1 - resource_split_tolerance))
            memory_split = int(memory_split * (1 - resource_split_tolerance))
            storage_split = int(storage_split * (1 - resource_split_tolerance))

        return AssignedMultiNodeWorkspaceResources(
            gpu_count=1,
            cpu_cores=cpu_split,
            memory_gb=memory_split,
            storage_gb=storage_split,
            total_nodes=total_nodes,
            gpu_vendor=", ".join(
                set([resource.gpu_vendor for resource in available_cluster_resources])
            ),
            heterogenous=len(
                set([resource.gpu_vendor for resource in available_cluster_resources])
            )
            > 1,
        )
