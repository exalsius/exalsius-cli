from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.models.cluster_create_response import ClusterCreateResponse
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

from exalsius.clusters.models import (
    ClustersAddNodeRequestDTO,
    ClustersCreateRequestDTO,
    ClustersDeleteNodeRequestDTO,
    ClustersDeleteRequestDTO,
    ClustersDeployRequestDTO,
    ClustersDownloadKubeConfigRequestDTO,
    ClustersGetRequestDTO,
    ClustersListRequestDTO,
    ClustersNodesRequestDTO,
    ClustersResourcesRequestDTO,
)
from exalsius.core.commons.commands.api import ExalsiusAPICommand


class ListClustersCommand(
    ExalsiusAPICommand[ClustersApi, ClustersListRequestDTO, ClustersListResponse]
):
    def __init__(self, request: ClustersListRequestDTO):
        self.request: ClustersListRequestDTO = request

    def _execute_api_call(self) -> ClustersListResponse:
        return self.api_client.list_clusters(self.request.status)


class GetClusterCommand(
    ExalsiusAPICommand[ClustersApi, ClustersGetRequestDTO, ClusterResponse]
):
    def _execute_api_call(self) -> ClusterResponse:
        return self.api_client.describe_cluster(self.request.cluster_id)


class DeleteClusterCommand(
    ExalsiusAPICommand[ClustersApi, ClustersDeleteRequestDTO, ClusterDeleteResponse]
):
    def _execute_api_call(self) -> ClusterDeleteResponse:
        return self.api_client.delete_cluster(self.request.cluster_id)


class CreateClusterCommand(
    ExalsiusAPICommand[ClustersApi, ClustersCreateRequestDTO, ClusterCreateResponse]
):
    def _execute_api_call(self) -> ClusterCreateResponse:
        return self.api_client.create_cluster(self.request.to_api_model())


class DeployClusterCommand(
    ExalsiusAPICommand[ClustersApi, ClustersDeployRequestDTO, ClusterDeployResponse]
):
    def _execute_api_call(self) -> ClusterDeployResponse:
        return self.api_client.deploy_cluster(self.request.cluster_id)


class GetClusterNodesCommand(
    ExalsiusAPICommand[ClustersApi, ClustersNodesRequestDTO, ClusterNodesResponse]
):
    def _execute_api_call(self) -> ClusterNodesResponse:
        return self.api_client.get_nodes(self.request.cluster_id)


class AddClusterNodeCommand(
    ExalsiusAPICommand[ClustersApi, ClustersAddNodeRequestDTO, ClusterNodesResponse]
):
    def _execute_api_call(self) -> ClusterNodesResponse:
        return self.api_client.add_nodes(
            self.request.cluster_id, self.request.to_api_model()
        )


class DeleteClusterNodeCommand(
    ExalsiusAPICommand[
        ClustersApi, ClustersDeleteNodeRequestDTO, ClusterNodeRemoveResponse
    ]
):
    def _execute_api_call(self) -> ClusterNodeRemoveResponse:
        return self.api_client.delete_node_from_cluster(
            self.request.cluster_id, self.request.node_id
        )


class GetClusterResourcesCommand(
    ExalsiusAPICommand[
        ClustersApi, ClustersResourcesRequestDTO, ClusterResourcesListResponse
    ]
):
    def _execute_api_call(self) -> ClusterResourcesListResponse:
        return self.api_client.get_cluster_resources(self.request.cluster_id)


class DownloadKubeConfigCommand(
    ExalsiusAPICommand[
        ClustersApi, ClustersDownloadKubeConfigRequestDTO, ClusterKubeconfigResponse
    ]
):
    def _execute_api_call(self) -> ClusterKubeconfigResponse:
        return self.api_client.get_cluster_kubeconfig(self.request.cluster_id)
