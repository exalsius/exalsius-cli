from typing import Optional

from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.models.cluster_add_node_request import ClusterAddNodeRequest
from exalsius_api_client.models.cluster_create_request import ClusterCreateRequest
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

from exls.clusters.core.domain import (
    ClusterStatus,
)
from exls.shared.adapters.gateway.sdk.command import (
    ExalsiusSdkCommand,
    UnexpectedSdkCommandResponseError,
)


class BaseClustersSdkCommand[T_Cmd_Return](
    ExalsiusSdkCommand[ClustersApi, T_Cmd_Return]
):
    """Base class for all clusters commands. Fixes the generic API type to ClustersApi."""

    pass


class ListClustersSdkCommand(BaseClustersSdkCommand[ClustersListResponse]):
    def __init__(self, api_client: ClustersApi, status: Optional[ClusterStatus]):
        super().__init__(api_client)
        self._status: Optional[ClusterStatus] = status

    def _execute_api_call(self) -> ClustersListResponse:
        response: ClustersListResponse = self.api_client.list_clusters(
            cluster_status=self._status
        )
        return response


class GetClusterSdkCommand(BaseClustersSdkCommand[ClusterResponse]):
    def __init__(self, api_client: ClustersApi, cluster_id: str):
        super().__init__(api_client)
        self._cluster_id: str = cluster_id

    def _execute_api_call(self) -> ClusterResponse:
        response: ClusterResponse = self.api_client.describe_cluster(
            cluster_id=self._cluster_id
        )
        return response


class DeleteClusterSdkCommand(BaseClustersSdkCommand[ClusterDeleteResponse]):
    def __init__(self, api_client: ClustersApi, cluster_id: str):
        super().__init__(api_client)
        self._cluster_id: str = cluster_id

    def _execute_api_call(self) -> ClusterDeleteResponse:
        response: ClusterDeleteResponse = self.api_client.delete_cluster(
            cluster_id=self._cluster_id
        )
        return response


class CreateClusterSdkCommand(BaseClustersSdkCommand[ClusterCreateResponse]):
    def __init__(self, api_client: ClustersApi, request: ClusterCreateRequest):
        super().__init__(api_client)
        self._request: ClusterCreateRequest = request

    def _execute_api_call(self) -> ClusterCreateResponse:
        response: ClusterCreateResponse = self.api_client.create_cluster(
            cluster_create_request=self._request
        )
        return response


class DeployClusterSdkCommand(BaseClustersSdkCommand[ClusterDeployResponse]):
    def __init__(self, api_client: ClustersApi, cluster_id: str):
        super().__init__(api_client)
        self._cluster_id: str = cluster_id

    def _execute_api_call(self) -> ClusterDeployResponse:
        response: ClusterDeployResponse = self.api_client.deploy_cluster(
            cluster_id=self._cluster_id
        )
        return response


class GetClusterNodesSdkCommand(BaseClustersSdkCommand[ClusterNodesResponse]):
    def __init__(self, api_client: ClustersApi, cluster_id: str):
        super().__init__(api_client)
        self._cluster_id: str = cluster_id

    def _execute_api_call(self) -> ClusterNodesResponse:
        response: ClusterNodesResponse = self.api_client.get_nodes(
            cluster_id=self._cluster_id
        )
        return response


class AddNodesSdkCommand(BaseClustersSdkCommand[ClusterNodesResponse]):
    def __init__(
        self, api_client: ClustersApi, cluster_id: str, request: ClusterAddNodeRequest
    ):
        super().__init__(api_client)
        self._cluster_id: str = cluster_id
        self._request: ClusterAddNodeRequest = request

    def _execute_api_call(self) -> ClusterNodesResponse:
        response: ClusterNodesResponse = self.api_client.add_nodes(
            cluster_id=self._cluster_id,
            cluster_add_node_request=self._request,
        )

        return response


class RemoveNodeSdkCommand(BaseClustersSdkCommand[ClusterNodeRemoveResponse]):
    def __init__(self, api_client: ClustersApi, cluster_id: str, node_id: str):
        super().__init__(api_client)
        self._cluster_id: str = cluster_id
        self._node_id: str = node_id

    def _execute_api_call(self) -> ClusterNodeRemoveResponse:
        response: ClusterNodeRemoveResponse = self.api_client.delete_node_from_cluster(
            cluster_id=self._cluster_id, node_id=self._node_id
        )
        return response


class GetClusterResourcesSdkCommand(
    BaseClustersSdkCommand[ClusterResourcesListResponse]
):
    def __init__(self, api_client: ClustersApi, cluster_id: str):
        super().__init__(api_client)
        self._cluster_id: str = cluster_id

    def _execute_api_call(self) -> ClusterResourcesListResponse:
        response: ClusterResourcesListResponse = self.api_client.get_cluster_resources(
            cluster_id=self._cluster_id
        )
        return response


class GetKubeconfigSdkCommand(BaseClustersSdkCommand[ClusterKubeconfigResponse]):
    def __init__(self, api_client: ClustersApi, cluster_id: str):
        super().__init__(api_client)
        self._cluster_id: str = cluster_id

    def _execute_api_call(self) -> ClusterKubeconfigResponse:
        response: ClusterKubeconfigResponse = self.api_client.get_cluster_kubeconfig(
            cluster_id=self._cluster_id
        )
        if not response.kubeconfig:
            raise UnexpectedSdkCommandResponseError(
                "Kubeconfig response is empty", self.__class__.__name__
            )

        return response


class GetDashboardUrlSdkCommand(BaseClustersSdkCommand[ClusterDashboardUrlResponse]):
    def __init__(self, api_client: ClustersApi, cluster_id: str):
        super().__init__(api_client)
        self._cluster_id: str = cluster_id

    def _execute_api_call(self) -> ClusterDashboardUrlResponse:
        response: ClusterDashboardUrlResponse = self.api_client.get_dashboard_url(
            cluster_id=self._cluster_id
        )
        return response
