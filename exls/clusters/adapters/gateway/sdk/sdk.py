from __future__ import annotations

import logging
from typing import List, Optional

from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.models.cluster import Cluster
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
from exalsius_api_client.models.cluster_resources_list_response_resources_inner import (
    ClusterResourcesListResponseResourcesInner,
)
from exalsius_api_client.models.cluster_response import ClusterResponse
from exalsius_api_client.models.clusters_list_response import ClustersListResponse

from exls.clusters.adapters.gateway.gateway import (
    ClusterCreateParameters,
    ClusterData,
    ClusterNodeRefData,
    ClusterNodeRefResourcesData,
    ClustersGateway,
    ResourcesData,
    get_cluster_labels,
)
from exls.clusters.adapters.gateway.sdk.commands import (
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
from exls.clusters.core.domain import (
    ClusterStatus,
)

logger = logging.getLogger(__name__)


def _cluster_data_from_sdk_model(sdk_model: Cluster) -> ClusterData:
    return ClusterData(
        id=sdk_model.id or "",
        name=sdk_model.name,
        status=sdk_model.cluster_status or "",
        type=sdk_model.cluster_type or "",
        created_at=sdk_model.created_at,
        updated_at=sdk_model.updated_at,
    )


def _cluster_node_ref_from_node_ids(
    control_plane_node_ids: List[str], worker_node_ids: List[str]
) -> List[ClusterNodeRefData]:
    return [
        ClusterNodeRefData(id=node_id, role="CONTROL_PLANE")
        for node_id in control_plane_node_ids
    ] + [ClusterNodeRefData(id=node_id, role="WORKER") for node_id in worker_node_ids]


def _cluster_node_ref_resources_data_from_sdk_model(
    sdk_model: ClusterResourcesListResponseResourcesInner,
) -> Optional[ClusterNodeRefResourcesData]:
    if sdk_model.node_id is None:
        logger.warning("Node ID is None for cluster node resources")
        return None
    if sdk_model.available is None:
        logger.warning(
            f"Available resources are None for cluster node {sdk_model.node_id}"
        )
        return None
    if sdk_model.occupied is None:
        logger.warning(
            f"Occupied resources are None for cluster node {sdk_model.node_id}"
        )
        return None

    available_resources: ResourcesData = ResourcesData(
        gpu_type=sdk_model.available.gpu_type or "",
        gpu_vendor=sdk_model.available.gpu_vendor or "",
        gpu_count=sdk_model.available.gpu_count or 0,
        cpu_cores=sdk_model.available.cpu_cores or 0,
        memory_gb=sdk_model.available.memory_gb or 0,
        storage_gb=sdk_model.available.storage_gb or 0,
    )
    occupied_resources: ResourcesData = ResourcesData(
        gpu_type=sdk_model.occupied.gpu_type or "",
        gpu_vendor=sdk_model.occupied.gpu_vendor or "",
        gpu_count=sdk_model.occupied.gpu_count or 0,
        cpu_cores=sdk_model.occupied.cpu_cores or 0,
        memory_gb=sdk_model.occupied.memory_gb or 0,
        storage_gb=sdk_model.occupied.storage_gb or 0,
    )
    return ClusterNodeRefResourcesData(
        node_id=sdk_model.node_id,
        node_name=sdk_model.node_name or "Unknown",
        free_resources=available_resources,
        occupied_resources=occupied_resources,
    )


class SdkClustersGateway(ClustersGateway):
    def __init__(self, clusters_api: ClustersApi):
        self._clusters_api = clusters_api

    def list(self, status: Optional[ClusterStatus]) -> List[ClusterData]:
        command: ListClustersSdkCommand = ListClustersSdkCommand(
            self._clusters_api,
            status=status.value if status and status != ClusterStatus.UNKNOWN else None,
        )
        response: ClustersListResponse = command.execute()
        clusters: List[ClusterData] = [
            _cluster_data_from_sdk_model(sdk_model=cluster)
            for cluster in response.clusters
        ]
        return clusters

    def get(self, cluster_id: str) -> ClusterData:
        command: GetClusterSdkCommand = GetClusterSdkCommand(
            self._clusters_api, cluster_id=cluster_id
        )
        response: ClusterResponse = command.execute()

        return _cluster_data_from_sdk_model(sdk_model=response.cluster)

    def delete(self, cluster_id: str) -> str:
        command: DeleteClusterSdkCommand = DeleteClusterSdkCommand(
            self._clusters_api, cluster_id=cluster_id
        )
        response: ClusterDeleteResponse = command.execute()
        return response.cluster_id

    def create(self, parameters: ClusterCreateParameters) -> str:
        sdk_request: SdkClusterCreateRequest = SdkClusterCreateRequest(
            name=parameters.name,
            cluster_type=parameters.type,
            cluster_labels=get_cluster_labels(parameters=parameters),
            vpn_cluster=parameters.enable_vpn,
            telemetry_enabled=parameters.enable_telemetry,
            colony_id=parameters.colony_id,
            to_be_deleted_at=parameters.to_be_deleted_at,
            control_plane_node_ids=parameters.control_plane_node_ids,
            worker_node_ids=parameters.worker_node_ids,
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

    def get_cluster_nodes(self, cluster_id: str) -> List[ClusterNodeRefData]:
        command: GetClusterNodesSdkCommand = GetClusterNodesSdkCommand(
            self._clusters_api, cluster_id=cluster_id
        )
        response: ClusterNodesResponse = command.execute()
        return _cluster_node_ref_from_node_ids(
            control_plane_node_ids=response.control_plane_node_ids,
            worker_node_ids=response.worker_node_ids,
        )

    def add_nodes_to_cluster(
        self, cluster_id: str, nodes_to_add: List[ClusterNodeRefData]
    ) -> List[ClusterNodeRefData]:
        # TODO: Sync with Dominik; nameing convention; why we can add multiple nodes at once
        #       but remove only one at a time?
        sdk_request: ClusterAddNodeRequest = ClusterAddNodeRequest(
            nodes_to_add=[
                ClusterNodeToAdd(node_id=node.id, node_role=node.role)
                for node in nodes_to_add
            ],
        )
        command: AddNodesSdkCommand = AddNodesSdkCommand(
            self._clusters_api,
            cluster_id=cluster_id,
            request=sdk_request,
        )
        response: ClusterNodesResponse = command.execute()

        return _cluster_node_ref_from_node_ids(
            control_plane_node_ids=response.control_plane_node_ids,
            worker_node_ids=response.worker_node_ids,
        )

    def remove_node_from_cluster(self, cluster_id: str, node_id: str) -> str:
        command: RemoveNodeSdkCommand = RemoveNodeSdkCommand(
            self._clusters_api, cluster_id=cluster_id, node_id=node_id
        )
        response: ClusterNodeRemoveResponse = command.execute()
        return response.node_id

    def get_cluster_resources(
        self, cluster_id: str
    ) -> List[ClusterNodeRefResourcesData]:
        command: GetClusterResourcesSdkCommand = GetClusterResourcesSdkCommand(
            self._clusters_api, cluster_id=cluster_id
        )
        response: ClusterResourcesListResponse = command.execute()

        cluster_node_resources: List[ClusterNodeRefResourcesData] = []
        for resource in response.resources:
            resource_model: Optional[ClusterNodeRefResourcesData] = (
                _cluster_node_ref_resources_data_from_sdk_model(sdk_model=resource)
            )
            if resource_model:
                cluster_node_resources.append(resource_model)
        return cluster_node_resources

    def load_kubeconfig(self, cluster_id: str) -> str:
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
