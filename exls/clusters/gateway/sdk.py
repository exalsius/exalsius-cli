from typing import Any, Dict, List

import yaml
from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.models.cluster import Cluster as SdkCluster
from exalsius_api_client.models.cluster_create_response import ClusterCreateResponse
from exalsius_api_client.models.cluster_dashboard_url_response import (
    ClusterDashboardUrlResponse,
)
from exalsius_api_client.models.cluster_delete_response import ClusterDeleteResponse
from exalsius_api_client.models.cluster_deploy_response import ClusterDeployResponse
from exalsius_api_client.models.cluster_kubeconfig_response import (
    ClusterKubeconfigResponse,
)
from exalsius_api_client.models.cluster_node_remove_response import (
    ClusterNodeRemoveResponse,
)
from exalsius_api_client.models.cluster_nodes_response import ClusterNodesResponse
from exalsius_api_client.models.cluster_resources_list_response import (
    ClusterResourcesListResponse,
)
from exalsius_api_client.models.cluster_response import ClusterResponse
from exalsius_api_client.models.clusters_list_response import ClustersListResponse

from exls.clusters.domain import (
    Cluster,
    ClusterNodeRef,
    ClusterNodeResources,
    Resources,
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
    GetDashboardUrlSdkCommand,
    GetKubeconfigSdkCommand,
    ListClustersSdkCommand,
    RemoveNodeSdkCommand,
)
from exls.clusters.gateway.dtos import (
    AddNodesParams,
    ClusterCreateParams,
    ClusterFilterParams,
    RemoveNodeParams,
)
from exls.core.commons.gateways.commands.sdk import UnexpectedSdkCommandResponseError


class ClustersGatewaySdk(ClustersGateway):
    def __init__(self, clusters_api: ClustersApi):
        self._clusters_api = clusters_api

    def _create_cluster_from_sdk_model(self, sdk_model: SdkCluster) -> Cluster:
        return Cluster(sdk_model=sdk_model)

    def list(self, cluster_filter_params: ClusterFilterParams) -> List[Cluster]:
        command: ListClustersSdkCommand = ListClustersSdkCommand(
            self._clusters_api, params=cluster_filter_params.status
        )
        response: ClustersListResponse = command.execute()
        return [
            self._create_cluster_from_sdk_model(sdk_model=cluster)
            for cluster in response.clusters
        ]

    def get(self, cluster_id: str) -> Cluster:
        command: GetClusterSdkCommand = GetClusterSdkCommand(
            self._clusters_api, params=cluster_id
        )
        response: ClusterResponse = command.execute()
        return self._create_cluster_from_sdk_model(sdk_model=response.cluster)

    def delete(self, cluster_id: str) -> str:
        command: DeleteClusterSdkCommand = DeleteClusterSdkCommand(
            self._clusters_api, cluster_id
        )
        response: ClusterDeleteResponse = command.execute()
        return response.cluster_id

    def create(self, cluster_create_params: ClusterCreateParams) -> str:
        command: CreateClusterSdkCommand = CreateClusterSdkCommand(
            self._clusters_api, params=cluster_create_params.to_sdk_request()
        )
        response: ClusterCreateResponse = command.execute()
        return response.cluster_id

    def deploy(self, cluster_id: str) -> str:
        command: DeployClusterSdkCommand = DeployClusterSdkCommand(
            self._clusters_api, params=cluster_id
        )
        response: ClusterDeployResponse = command.execute()
        return response.cluster_id

    def get_cluster_nodes(self, cluster_id: str) -> List[ClusterNodeRef]:
        command: GetClusterNodesSdkCommand = GetClusterNodesSdkCommand(
            self._clusters_api, params=cluster_id
        )
        response: ClusterNodesResponse = command.execute()
        return [
            ClusterNodeRef(node_id=node_id, role="WORKER")
            for node_id in response.worker_node_ids
        ] + [
            ClusterNodeRef(node_id=node_id, role="CONTROL_PLANE")
            for node_id in response.control_plane_node_ids
        ]

    def add_nodes_to_cluster(
        self, add_nodes_params: AddNodesParams
    ) -> List[ClusterNodeRef]:
        command: AddNodesSdkCommand = AddNodesSdkCommand(
            self._clusters_api, add_nodes_params
        )
        response: ClusterNodesResponse = command.execute()

        return [
            ClusterNodeRef(node_id=node_id, role="WORKER")
            for node_id in response.worker_node_ids
        ] + [
            ClusterNodeRef(node_id=node_id, role="CONTROL_PLANE")
            for node_id in response.control_plane_node_ids
        ]

    def remove_node_from_cluster(self, remove_node_params: RemoveNodeParams) -> str:
        command: RemoveNodeSdkCommand = RemoveNodeSdkCommand(
            self._clusters_api, remove_node_params
        )
        response: ClusterNodeRemoveResponse = command.execute()
        return response.node_id

    def get_cluster_resources(self, cluster_id: str) -> List[ClusterNodeResources]:
        command: GetClusterResourcesSdkCommand = GetClusterResourcesSdkCommand(
            self._clusters_api, params=cluster_id
        )
        response: ClusterResourcesListResponse = command.execute()

        cluster_node_resources: List[ClusterNodeResources] = []
        for resource in response.resources:
            if resource.node_id is None:
                raise UnexpectedSdkCommandResponseError(
                    "Node ID is None", self.__class__.__name__
                )
            if resource.available is None:
                raise UnexpectedSdkCommandResponseError(
                    "Available resources are None", self.__class__.__name__
                )
            if resource.occupied is None:
                raise UnexpectedSdkCommandResponseError(
                    "Occupied resources are None", self.__class__.__name__
                )
            cluster_node_resources.append(
                ClusterNodeResources(
                    node_id=resource.node_id,
                    free_resources=Resources(sdk_model=resource.available),
                    occupied_resources=Resources(sdk_model=resource.occupied),
                )
            )
        return cluster_node_resources

    def get_kubeconfig(self, cluster_id: str) -> Dict[str, Any]:
        command: GetKubeconfigSdkCommand = GetKubeconfigSdkCommand(
            self._clusters_api, cluster_id
        )
        response: ClusterKubeconfigResponse = command.execute()
        try:
            kubeconfig_content: Dict[str, Any] = yaml.safe_load(response.kubeconfig)
            return kubeconfig_content
        except yaml.YAMLError as e:
            raise UnexpectedSdkCommandResponseError(
                f"Failed to parse kubeconfig: {str(e)}", self.__class__.__name__
            )

    def get_dashboard_url(self, cluster_id: str) -> str:
        command: GetDashboardUrlSdkCommand = GetDashboardUrlSdkCommand(
            self._clusters_api, cluster_id
        )
        response: ClusterDashboardUrlResponse = command.execute()
        return response.url
