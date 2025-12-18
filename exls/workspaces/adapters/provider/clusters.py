from typing import List, Optional

from exls.workspaces.core.ports.provider import IClustersProvider

from exls.clusters.core.domain import Cluster
from exls.clusters.core.service import ClustersService
from exls.workspaces.core.domain import (
    AvailableClusterNodeResources,
    WorkspaceCluster,
    WorkspaceClusterStatus,
    WorkspaceGPUVendor,
)


class ClustersDomainProvider(IClustersProvider):
    def __init__(self, clusters_service: ClustersService):
        self.clusters_service: ClustersService = clusters_service

    def list_clusters(self) -> List[WorkspaceCluster]:
        clusters: List[Cluster] = self.clusters_service.list_clusters()
        return [
            WorkspaceCluster(
                id=cluster.id,
                name=cluster.name,
                status=WorkspaceClusterStatus.from_str(cluster.status.value),
            )
            for cluster in clusters
        ]

    def get_cluster(self, cluster_id: str) -> WorkspaceCluster:
        cluster: Cluster = self.clusters_service.get_cluster(cluster_id=cluster_id)
        return WorkspaceCluster(
            id=cluster.id,
            name=cluster.name,
            status=WorkspaceClusterStatus.from_str(cluster.status.value),
        )

    def get_cluster_resources(
        self, cluster_id: str
    ) -> List[AvailableClusterNodeResources]:
        cluster: Cluster = self.clusters_service.get_cluster(cluster_id=cluster_id)
        available_cluster_resources: List[AvailableClusterNodeResources] = []
        for resource in cluster.nodes:
            node_name: str = resource.hostname
            node_id: str = resource.id
            node_endpoint: Optional[str] = resource.endpoint
            available_cluster_resources.append(
                AvailableClusterNodeResources(
                    node_id=node_id,
                    node_name=node_name,
                    node_endpoint=node_endpoint,
                    gpu_type=resource.free_resources.gpu_type,
                    gpu_vendor=WorkspaceGPUVendor.from_str(
                        resource.free_resources.gpu_vendor
                    ),
                    gpu_count=resource.free_resources.gpu_count,
                    cpu_cores=resource.free_resources.cpu_cores,
                    memory_gb=resource.free_resources.memory_gb,
                    storage_gb=resource.free_resources.storage_gb,
                )
            )
        return available_cluster_resources
