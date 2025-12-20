import logging
from typing import Dict, List, Optional

from exls.clusters.adapters.gateway.gateway import (
    ClusterData,
    ClusterNodeRefData,
    ClusterNodeRefResourcesData,
    ClustersGateway,
    ResourcesData,
)
from exls.clusters.core.domain import (
    Cluster,
    ClusterNode,
    ClusterNodeResources,
    ClusterNodeRole,
    ClusterNodeStatus,
    ClusterStatus,
    ClusterType,
)
from exls.clusters.core.ports.operations import ClusterOperations
from exls.clusters.core.ports.provider import ClusterNodeData, NodesProvider
from exls.clusters.core.ports.repository import (
    ClusterCreateParameters,
    ClusterRepository,
)
from exls.clusters.core.results import ClusterScaleIssue, ClusterScaleResult
from exls.shared.core.exceptions import ExalsiusError
from exls.shared.core.ports.command import CommandError

logger = logging.getLogger(__name__)


class ClusterLoadingError(ExalsiusError):
    pass


def _map_resources(resources: ResourcesData) -> ClusterNodeResources:
    return ClusterNodeResources(
        gpu_type=resources.gpu_type,
        gpu_vendor=resources.gpu_vendor,
        gpu_count=resources.gpu_count,
        cpu_cores=resources.cpu_cores,
        memory_gb=resources.memory_gb,
        storage_gb=resources.storage_gb,
    )


def _map_cluster_node(
    cluster_node_ref: ClusterNodeRefData,
    cluster_node_resource: ClusterNodeRefResourcesData,
    cluster_node_data: Optional[ClusterNodeData],
) -> ClusterNode:
    if cluster_node_data:
        return ClusterNode(
            id=cluster_node_ref.id,
            role=ClusterNodeRole.from_str(cluster_node_ref.role),
            hostname=cluster_node_data.hostname,
            username=cluster_node_data.username,
            ssh_key_id=cluster_node_data.ssh_key_id,
            status=ClusterNodeStatus.from_str(cluster_node_data.status),
            endpoint=cluster_node_data.endpoint or "",
            free_resources=_map_resources(cluster_node_resource.free_resources),
            occupied_resources=_map_resources(cluster_node_resource.occupied_resources),
        )
    else:
        return ClusterNode(
            id=cluster_node_ref.id,
            role=ClusterNodeRole.from_str(cluster_node_ref.role),
            hostname=cluster_node_resource.node_name,
            username="Unknown",
            ssh_key_id="Unknown",
            status=ClusterNodeStatus.UNKNOWN,
            endpoint="",
            free_resources=_map_resources(cluster_node_resource.free_resources),
            occupied_resources=_map_resources(cluster_node_resource.occupied_resources),
        )


class ClusterAdapter(ClusterRepository, ClusterOperations):
    def __init__(self, cluster_gateway: ClustersGateway, nodes_provider: NodesProvider):
        self._cluster_gateway: ClustersGateway = cluster_gateway
        self._nodes_provider: NodesProvider = nodes_provider

    def _load_cluster_nodes(self, cluster_id: str) -> List[ClusterNode]:
        cluster_node_refs: List[ClusterNodeRefData] = (
            self._cluster_gateway.get_cluster_nodes(cluster_id=cluster_id)
        )
        cluster_node_resources: List[ClusterNodeRefResourcesData] = (
            self._cluster_gateway.get_cluster_resources(cluster_id=cluster_id)
        )
        nodes_data: List[ClusterNodeData] = self._nodes_provider.list_nodes()

        cluster_node_resource_map: Dict[str, ClusterNodeRefResourcesData] = {
            resource.node_id: resource for resource in cluster_node_resources
        }
        nodes_data_map: Dict[str, ClusterNodeData] = {
            node.id: node for node in nodes_data
        }

        nodes: List[ClusterNode] = []
        for cluster_node_resource in cluster_node_refs:
            if cluster_node_resource.id not in cluster_node_resource_map:
                raise ClusterLoadingError(
                    f"Resources cannot be loaded for cluster node {cluster_node_resource.id}"
                )
            if cluster_node_resource.id not in nodes_data_map:
                logger.warning(
                    f"Node {cluster_node_resource.id} not found in cluster node resources or nodes data"
                )

            cluster_node: ClusterNode = _map_cluster_node(
                cluster_node_ref=cluster_node_resource,
                cluster_node_resource=cluster_node_resource_map[
                    cluster_node_resource.id
                ],
                cluster_node_data=nodes_data_map.get(cluster_node_resource.id, None),
            )
            nodes.append(cluster_node)

        return nodes

    def list(self, status: Optional[ClusterStatus]) -> List[Cluster]:
        cluster_data_list: List[ClusterData] = self._cluster_gateway.list(status=status)
        clusters: List[Cluster] = []
        for cluster_data in cluster_data_list:
            clusters.append(
                Cluster(
                    id=cluster_data.id,
                    name=cluster_data.name,
                    status=ClusterStatus.from_str(cluster_data.status),
                    type=ClusterType.from_str(cluster_data.type),
                    created_at=cluster_data.created_at,
                    updated_at=cluster_data.updated_at,
                    nodes=self._load_cluster_nodes(cluster_id=cluster_data.id),
                )
            )
        if status:
            return [cluster for cluster in clusters if cluster.status == status]
        else:
            return clusters

    def get(self, cluster_id: str) -> Cluster:
        cluster_data: ClusterData = self._cluster_gateway.get(cluster_id=cluster_id)
        nodes: List[ClusterNode] = self._load_cluster_nodes(cluster_id=cluster_id)
        return Cluster(
            id=cluster_data.id,
            name=cluster_data.name,
            status=ClusterStatus.from_str(cluster_data.status),
            type=ClusterType.from_str(cluster_data.type),
            created_at=cluster_data.created_at,
            updated_at=cluster_data.updated_at,
            nodes=nodes,
        )

    def create(self, parameters: ClusterCreateParameters) -> str:
        return self._cluster_gateway.create(parameters=parameters)

    def delete(self, cluster_id: str) -> str:
        return self._cluster_gateway.delete(cluster_id=cluster_id)

    def deploy(self, cluster_id: str) -> str:
        return self._cluster_gateway.deploy(cluster_id=cluster_id)

    def scale_up(
        self, cluster_id: str, nodes_to_add: List[ClusterNode]
    ) -> ClusterScaleResult:
        node_map: Dict[str, ClusterNode] = {node.id: node for node in nodes_to_add}
        nodes_to_add_ref_data: List[ClusterNodeRefData] = [
            ClusterNodeRefData(id=node.id, role=node.role.value)
            for node in nodes_to_add
        ]
        added_nodes_ref_data: List[ClusterNodeRefData] = (
            self._cluster_gateway.add_nodes_to_cluster(
                cluster_id=cluster_id, nodes_to_add=nodes_to_add_ref_data
            )
        )
        # TODO: Sync with Dominik to learn how to handle issues here
        added_nodes: List[ClusterNode] = [
            node_map[node.id] for node in added_nodes_ref_data if node.id in node_map
        ]
        return ClusterScaleResult(nodes=added_nodes)

    def scale_down(
        self, cluster_id: str, nodes_to_remove: List[ClusterNode]
    ) -> ClusterScaleResult:
        node_map: Dict[str, ClusterNode] = {node.id: node for node in nodes_to_remove}
        nodes_to_remove_ref_data: List[ClusterNodeRefData] = [
            ClusterNodeRefData(id=node.id, role=node.role.value)
            for node in nodes_to_remove
        ]

        removed_nodes: List[ClusterNode] = []
        issues: List[ClusterScaleIssue] = []
        for node_to_remove_ref_data in nodes_to_remove_ref_data:
            try:
                removed_node_id: str = self._cluster_gateway.remove_node_from_cluster(
                    cluster_id=cluster_id, node_id=node_to_remove_ref_data.id
                )
                if removed_node_id in node_map:
                    removed_nodes.append(node_map[removed_node_id])
                else:
                    issues.append(
                        ClusterScaleIssue(
                            node=node_map[node_to_remove_ref_data.id],
                            error_message=f"Node {removed_node_id} not found",
                        )
                    )
            except CommandError as e:
                issues.append(
                    ClusterScaleIssue(
                        node=node_map[node_to_remove_ref_data.id], error_message=str(e)
                    )
                )
        return ClusterScaleResult(nodes=removed_nodes, issues=issues)

    def load_kubeconfig(self, cluster_id: str) -> str:
        return self._cluster_gateway.load_kubeconfig(cluster_id=cluster_id)

    def get_dashboard_url(self, cluster_id: str) -> str:
        return self._cluster_gateway.get_dashboard_url(cluster_id=cluster_id)
