from typing import Dict, List, Optional

from pydantic.types import StrictFloat

from exls.config import ConfigWorkspaceCreationPolling
from exls.shared.adapters.decorators import handle_service_layer_errors
from exls.shared.core.polling import poll_until
from exls.shared.core.service import ServiceError
from exls.workspaces.core.domain import (
    WorkerGroupResources,
    Workspace,
    WorkspaceCluster,
    WorkspaceClusterStatus,
    WorkspaceStatus,
    WorkspaceTemplate,
)
from exls.workspaces.core.ports.operations import WorkspaceOperations
from exls.workspaces.core.ports.providers import (
    ClustersProvider,
    WorkspaceTemplatesProvider,
)
from exls.workspaces.core.ports.repository import WorkspaceRepository
from exls.workspaces.core.requests import (
    DeployWorkspaceRequest,
    WorkerResources,
)


class WorkspacesService:
    def __init__(
        self,
        workspace_creation_polling_config: ConfigWorkspaceCreationPolling,
        workspaces_operations: WorkspaceOperations,
        workspaces_repository: WorkspaceRepository,
        clusters_provider: ClustersProvider,
        workspace_templates_provider: WorkspaceTemplatesProvider,
    ):
        self._workspace_creation_polling_config: ConfigWorkspaceCreationPolling = (
            workspace_creation_polling_config
        )
        self._workspaces_operations: WorkspaceOperations = workspaces_operations
        self._workspaces_repository: WorkspaceRepository = workspaces_repository
        self._clusters_provider: ClustersProvider = clusters_provider
        self._workspace_templates_provider: WorkspaceTemplatesProvider = (
            workspace_templates_provider
        )

        self._cached_clusters: Dict[str, WorkspaceCluster] = {}

    def _get_workspace_cluster(self, cluster_id: str) -> WorkspaceCluster:
        if cluster_id not in self._cached_clusters:
            self._cached_clusters[cluster_id] = self._clusters_provider.get_cluster(
                cluster_id=cluster_id
            )
        return self._cached_clusters[cluster_id]

    def _get_and_validate_cluster(self, cluster_id: str) -> WorkspaceCluster:
        cluster: WorkspaceCluster = self._get_workspace_cluster(cluster_id=cluster_id)
        if cluster.status != WorkspaceClusterStatus.READY:
            raise ServiceError(
                f"Cluster {cluster.name} ({cluster_id}) is not ready. Current status: {cluster.status}"
            )
        return cluster

    @handle_service_layer_errors("listing workspaces")
    def list_workspaces(self, cluster_id: Optional[str] = None) -> List[Workspace]:
        return self._workspaces_repository.list(cluster_id=cluster_id)

    @handle_service_layer_errors("getting workspace")
    def get_workspace(self, workspace_id: str) -> Workspace:
        return self._workspaces_repository.get(workspace_id=workspace_id)

    @handle_service_layer_errors("deleting workspace")
    def delete_workspaces(self, workspace_ids: List[str]) -> None:
        for workspace_id in workspace_ids:
            self._workspaces_repository.delete(workspace_id=workspace_id)

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
        cluster: WorkspaceCluster = self._get_workspace_cluster(
            cluster_id=request.cluster_id
        )
        # TODO: imporve error message to show which resources are missing
        if not cluster.has_enough_resources(requested_resources=request.resources):
            raise ServiceError(
                f"Cluster {cluster.name} ({cluster.id}) does not have enough resources. "
                f"Needs at least {request.resources.gpu_count} GPUs. Has {cluster.available_resources} GPUs."
            )

        workspace_id: str = self._workspaces_operations.deploy(parameters=request)

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
        self,
        cluster_id: str,
        num_gpus: int,
        resource_split_tolerance: StrictFloat = 0.1,
    ) -> WorkerResources:
        cluster: WorkspaceCluster = self._get_and_validate_cluster(
            cluster_id=cluster_id
        )

        # TODO: improve error message to show which resources are missing
        resource_partition: Optional[WorkerResources] = (
            cluster.get_resource_partition_for_single_worker(
                num_requested_gpus=num_gpus,
                resource_split_tolerance=resource_split_tolerance,
            )
        )
        if resource_partition is None:
            raise ServiceError(
                f"Cluster {cluster.name} ({cluster_id}) does not have a node with at least {num_gpus} requested "
                f"GPU{'' if num_gpus == 1 else 's'}."
            )
        return resource_partition

    @handle_service_layer_errors("getting resources for distributed training workspace")
    def get_resources_for_multi_node_workspace(
        self, cluster_id: str, resource_split_tolerance: StrictFloat = 0.1
    ) -> List[WorkerGroupResources]:
        cluster: WorkspaceCluster = self._get_and_validate_cluster(
            cluster_id=cluster_id
        )
        total_gpus: int = sum(
            [resource.gpu_count for resource in cluster.available_resources]
        )
        if total_gpus < 2:
            raise ServiceError(
                (
                    f"Cluster {cluster.name} ({cluster_id}) does not have enough "
                    "available GPUs to deploy a distributed training workspace. "
                    f"Needs at least 2 GPUs. Has {total_gpus} GPUs."
                )
            )

        num_workers: int = total_gpus
        resource_partitions: List[WorkerGroupResources] = (
            cluster.get_resource_partition_for_worker_groups(
                num_workers=num_workers,
                gpu_vendor="auto",
                resource_split_tolerance=resource_split_tolerance,
            )
        )
        return resource_partitions
