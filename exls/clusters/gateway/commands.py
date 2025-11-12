from typing import Optional

from exalsius_api_client.api.clusters_api import ClustersApi
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

from exls.clusters.gateway.dtos import (
    AddNodesParams,
    RemoveNodeParams,
)
from exls.core.commons.gateways.commands.sdk import (
    ExalsiusSdkCommand,
    UnexpectedSdkCommandResponseError,
)


class BaseClustersSdkCommand[T_Cmd_Params, T_Cmd_Return](
    ExalsiusSdkCommand[ClustersApi, T_Cmd_Params, T_Cmd_Return]
):
    """Base class for all clusters commands. Fixes the generic API type to ClustersApi."""

    pass


class ListClustersSdkCommand(
    BaseClustersSdkCommand[Optional[str], ClustersListResponse]
):
    def _execute_api_call(self, params: Optional[str]) -> ClustersListResponse:
        response: ClustersListResponse = self.api_client.list_clusters(
            cluster_status=params
        )
        return response


class GetClusterSdkCommand(BaseClustersSdkCommand[str, ClusterResponse]):
    def _execute_api_call(self, params: Optional[str]) -> ClusterResponse:
        assert params is not None
        response: ClusterResponse = self.api_client.describe_cluster(cluster_id=params)
        return response


class DeleteClusterSdkCommand(BaseClustersSdkCommand[str, ClusterDeleteResponse]):
    def _execute_api_call(self, params: Optional[str]) -> ClusterDeleteResponse:
        assert params is not None
        response: ClusterDeleteResponse = self.api_client.delete_cluster(
            cluster_id=params
        )
        return response


class CreateClusterSdkCommand(
    BaseClustersSdkCommand[ClusterCreateRequest, ClusterCreateResponse]
):
    def _execute_api_call(
        self, params: Optional[ClusterCreateRequest]
    ) -> ClusterCreateResponse:
        assert params is not None
        response: ClusterCreateResponse = self.api_client.create_cluster(
            cluster_create_request=params
        )
        return response


class DeployClusterSdkCommand(BaseClustersSdkCommand[str, ClusterDeployResponse]):
    def _execute_api_call(self, params: Optional[str]) -> ClusterDeployResponse:
        assert params is not None
        response: ClusterDeployResponse = self.api_client.deploy_cluster(
            cluster_id=params
        )
        return response


class GetClusterNodesSdkCommand(BaseClustersSdkCommand[str, ClusterNodesResponse]):
    def _execute_api_call(self, params: Optional[str]) -> ClusterNodesResponse:
        assert params is not None
        response: ClusterNodesResponse = self.api_client.get_nodes(cluster_id=params)
        return response


class AddNodesSdkCommand(BaseClustersSdkCommand[AddNodesParams, ClusterNodesResponse]):
    def _execute_api_call(
        self, params: Optional[AddNodesParams]
    ) -> ClusterNodesResponse:
        assert params is not None
        response: ClusterNodesResponse = self.api_client.add_nodes(
            cluster_id=params.cluster_id,
            cluster_add_node_request=params.to_sdk_request(),
        )

        return response


class RemoveNodeSdkCommand(
    BaseClustersSdkCommand[RemoveNodeParams, ClusterNodeRemoveResponse]
):
    def _execute_api_call(
        self, params: Optional[RemoveNodeParams]
    ) -> ClusterNodeRemoveResponse:
        assert params is not None
        response: ClusterNodeRemoveResponse = self.api_client.delete_node_from_cluster(
            cluster_id=params.cluster_id, node_id=params.node_id
        )
        return response


class GetClusterResourcesSdkCommand(
    BaseClustersSdkCommand[str, ClusterResourcesListResponse]
):
    def _execute_api_call(self, params: Optional[str]) -> ClusterResourcesListResponse:
        assert params is not None
        response: ClusterResourcesListResponse = self.api_client.get_cluster_resources(
            cluster_id=params
        )
        return response


class GetKubeconfigSdkCommand(BaseClustersSdkCommand[str, ClusterKubeconfigResponse]):
    def _execute_api_call(self, params: Optional[str]) -> ClusterKubeconfigResponse:
        assert params is not None
        response: ClusterKubeconfigResponse = self.api_client.get_cluster_kubeconfig(
            cluster_id=params
        )
        if not response.kubeconfig:
            raise UnexpectedSdkCommandResponseError(
                "Kubeconfig response is empty", self.__class__.__name__
            )

        return response


class GetDashboardUrlSdkCommand(
    BaseClustersSdkCommand[str, ClusterDashboardUrlResponse]
):
    def _execute_api_call(self, params: Optional[str]) -> ClusterDashboardUrlResponse:
        assert params is not None
        response: ClusterDashboardUrlResponse = self.api_client.get_dashboard_url(
            cluster_id=params
        )
        return response
