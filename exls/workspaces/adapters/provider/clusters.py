from typing import List

from exls.clusters.core.domain import Cluster, ClusterNodeResources
from exls.clusters.core.service import ClustersService
from exls.workspaces.core.domain import (
    AvailableClusterResources,
    WorkspaceCluster,
    WorkspaceClusterStatus,
)
from exls.workspaces.core.ports.provider import IClustersProvider


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

    def get_cluster_resources(self, cluster_id: str) -> List[AvailableClusterResources]:
        cluster_node_resources: List[ClusterNodeResources] = (
            self.clusters_service.get_cluster_resources(cluster_id=cluster_id)
        )
        return [
            AvailableClusterResources(
                node_id=resource.cluster_node.id,
                node_name=resource.cluster_node.hostname,
                gpu_type=resource.free_resources.gpu_type,
                gpu_vendor=resource.free_resources.gpu_vendor,
                gpu_count=resource.free_resources.gpu_count,
                cpu_cores=resource.free_resources.cpu_cores,
                memory_gb=resource.free_resources.memory_gb,
                storage_gb=resource.free_resources.storage_gb,
            )
            for resource in cluster_node_resources
        ]
