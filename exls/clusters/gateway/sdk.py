from typing import Any, Dict, List

from exalsius_api_client.api.clusters_api import ClustersApi

from exls.clusters.domain import (
    AddNodesParams,
    Cluster,
    ClusterCreateParams,
    ClusterFilterParams,
    ClusterNodeRef,
    ClusterNodeResources,
    RemoveNodeParams,
)
from exls.clusters.gateway.base import ClustersGateway
from exls.clusters.gateway.commands import (
    AddNodesSdkCommand,
    CreateClusterSdkCommand,
    DeleteClusterSdkCommand,
    DeployClusterSdkCommand,
    GetClusterNodesSdkCommand,
    GetClusterResourcesSdkCommand,
    GetClusterSdkCommand,
    GetKubeconfigSdkCommand,
    ListClustersSdkCommand,
    RemoveNodeSdkCommand,
)


class ClustersGatewaySdk(ClustersGateway):
    def __init__(self, clusters_api: ClustersApi):
        self._clusters_api = clusters_api

    def list(self, cluster_filter_params: ClusterFilterParams) -> List[Cluster]:
        command = ListClustersSdkCommand(self._clusters_api, cluster_filter_params)
        response: List[Cluster] = command.execute()
        return response

    def get(self, cluster_id: str) -> Cluster:
        command = GetClusterSdkCommand(self._clusters_api, cluster_id)
        response: Cluster = command.execute()
        return response

    def delete(self, cluster_id: str) -> str:
        command = DeleteClusterSdkCommand(self._clusters_api, cluster_id)
        response: str = command.execute()
        return response

    def create(self, cluster_create_params: ClusterCreateParams) -> str:
        command = CreateClusterSdkCommand(self._clusters_api, cluster_create_params)
        response: str = command.execute()
        return response

    def deploy(self, cluster_id: str) -> str:
        command = DeployClusterSdkCommand(self._clusters_api, cluster_id)
        command.execute()
        return cluster_id

    def get_cluster_nodes(self, cluster_id: str) -> List[ClusterNodeRef]:
        cmd_get_nodes = GetClusterNodesSdkCommand(self._clusters_api, cluster_id)
        cluster_node_refs: List[ClusterNodeRef] = cmd_get_nodes.execute()
        return cluster_node_refs

    def add_nodes_to_cluster(
        self, add_nodes_params: AddNodesParams
    ) -> List[ClusterNodeRef]:
        command = AddNodesSdkCommand(self._clusters_api, add_nodes_params)
        response: List[ClusterNodeRef] = command.execute()

        return response

    def remove_node_from_cluster(self, remove_node_params: RemoveNodeParams) -> str:
        command = RemoveNodeSdkCommand(self._clusters_api, remove_node_params)
        response: str = command.execute()
        return response

    def get_cluster_resources(self, cluster_id: str) -> List[ClusterNodeResources]:
        command = GetClusterResourcesSdkCommand(self._clusters_api, cluster_id)
        response: List[ClusterNodeResources] = command.execute()
        return response

    def get_kubeconfig(self, cluster_id: str) -> Dict[str, Any]:
        command = GetKubeconfigSdkCommand(self._clusters_api, cluster_id)
        response: Dict[str, Any] = command.execute()
        return response
