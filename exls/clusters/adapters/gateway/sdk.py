from typing import List, Optional

from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.models.cluster_add_node_request import ClusterAddNodeRequest
from exalsius_api_client.models.cluster_create_request import (
    ClusterCreateRequest as SdkClusterCreateRequest,
)
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
from exalsius_api_client.models.cluster_node_to_add import ClusterNodeToAdd
from exalsius_api_client.models.cluster_nodes_response import ClusterNodesResponse
from exalsius_api_client.models.cluster_resources_list_response import (
    ClusterResourcesListResponse,
)
from exalsius_api_client.models.cluster_response import ClusterResponse
from exalsius_api_client.models.clusters_list_response import ClustersListResponse

from exls.clusters.adapters.gateway.commands import (
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
from exls.clusters.adapters.gateway.mappers import (
    cluster_from_sdk_model,
    cluster_node_ref_from_node_ids,
    resources_from_sdk_model,
)
from exls.clusters.core.domain import (
    AddNodesRequest,
    Cluster,
    ClusterCreateRequest,
    ClusterFilterCriteria,
    ClusterNodeResources,
    NodeRef,
    RemoveNodesRequest,
)
from exls.clusters.core.ports import IClustersGateway
from exls.shared.adapters.gateway.sdk.service import create_api_client


class ClustersGatewaySdk(IClustersGateway):
    def __init__(self, clusters_api: ClustersApi):
        self._clusters_api = clusters_api

    def list(self, criteria: ClusterFilterCriteria) -> List[Cluster]:
        command: ListClustersSdkCommand = ListClustersSdkCommand(
            self._clusters_api, status=criteria.status
        )
        response: ClustersListResponse = command.execute()
        clusters: List[Cluster] = [
            cluster_from_sdk_model(sdk_model=cluster) for cluster in response.clusters
        ]
        return clusters

    def get(self, cluster_id: str) -> Cluster:
        command: GetClusterSdkCommand = GetClusterSdkCommand(
            self._clusters_api, cluster_id=cluster_id
        )
        response: ClusterResponse = command.execute()

        return cluster_from_sdk_model(sdk_model=response.cluster)

    def delete(self, cluster_id: str) -> str:
        command: DeleteClusterSdkCommand = DeleteClusterSdkCommand(
            self._clusters_api, cluster_id=cluster_id
        )
        response: ClusterDeleteResponse = command.execute()
        return response.cluster_id

    def create(self, request: ClusterCreateRequest) -> str:
        sdk_request: SdkClusterCreateRequest = SdkClusterCreateRequest(
            name=request.name,
            cluster_type=request.cluster_type,
            cluster_labels=request.cluster_labels,
            colony_id=request.colony_id,
            to_be_deleted_at=request.to_be_deleted_at,
            control_plane_node_ids=request.control_plane_node_ids,
            worker_node_ids=request.worker_node_ids,
        )
        command: CreateClusterSdkCommand = CreateClusterSdkCommand(
            self._clusters_api,
            request=sdk_request,
        )
        response: ClusterCreateResponse = command.execute()
        return response.cluster_id

    def deploy(self, cluster_id: str) -> str:
        command: DeployClusterSdkCommand = DeployClusterSdkCommand(
            self._clusters_api, cluster_id=cluster_id
        )
        response: ClusterDeployResponse = command.execute()
        return response.cluster_id

    def get_cluster_nodes(self, cluster_id: str) -> List[NodeRef]:
        command: GetClusterNodesSdkCommand = GetClusterNodesSdkCommand(
            self._clusters_api, cluster_id=cluster_id
        )
        response: ClusterNodesResponse = command.execute()
        return cluster_node_ref_from_node_ids(
            response.worker_node_ids, response.control_plane_node_ids
        )

    def add_nodes_to_cluster(self, request: AddNodesRequest) -> List[NodeRef]:
        sdk_request: ClusterAddNodeRequest = ClusterAddNodeRequest(
            nodes_to_add=[
                ClusterNodeToAdd(node_id=n.id, node_role=n.role.value)
                for n in request.nodes_to_add
            ],
        )
        command: AddNodesSdkCommand = AddNodesSdkCommand(
            self._clusters_api,
            cluster_id=request.cluster_id,
            request=sdk_request,
        )
        response: ClusterNodesResponse = command.execute()

        return cluster_node_ref_from_node_ids(
            response.worker_node_ids, response.control_plane_node_ids
        )

    def remove_nodes_from_cluster(self, request: RemoveNodesRequest) -> List[str]:
        commands: List[RemoveNodeSdkCommand] = [
            RemoveNodeSdkCommand(
                self._clusters_api,
                cluster_id=request.cluster_id,
                node_id=n.id,
            )
            for n in request.nodes_to_remove
        ]
        responses: List[ClusterNodeRemoveResponse] = [
            command.execute() for command in commands
        ]
        return [response.node_id for response in responses]

    def get_cluster_resources(self, cluster_id: str) -> List[ClusterNodeResources]:
        command: GetClusterResourcesSdkCommand = GetClusterResourcesSdkCommand(
            self._clusters_api, cluster_id=cluster_id
        )
        response: ClusterResourcesListResponse = command.execute()

        cluster_node_resources: List[ClusterNodeResources] = []
        for resource in response.resources:
            resource_model: Optional[ClusterNodeResources] = resources_from_sdk_model(
                sdk_model=resource
            )
            if resource_model:
                cluster_node_resources.append(resource_model)
        return cluster_node_resources

    def get_kubeconfig(self, cluster_id: str) -> str:
        command: GetKubeconfigSdkCommand = GetKubeconfigSdkCommand(
            self._clusters_api, cluster_id
        )
        response: ClusterKubeconfigResponse = command.execute()
        return response.kubeconfig

    def get_dashboard_url(self, cluster_id: str) -> str:
        command: GetDashboardUrlSdkCommand = GetDashboardUrlSdkCommand(
            self._clusters_api, cluster_id
        )
        response: ClusterDashboardUrlResponse = command.execute()
        return response.url


def create_clusters_gateway(backend_host: str, access_token: str) -> IClustersGateway:
    clusters_api: ClustersApi = ClustersApi(
        create_api_client(backend_host=backend_host, access_token=access_token)
    )
    return ClustersGatewaySdk(clusters_api=clusters_api)
