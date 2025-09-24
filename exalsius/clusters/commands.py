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
from exalsius_api_client.models.credentials_list_response import CredentialsListResponse

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
    ListCloudCredentialsRequestDTO,
)
from exalsius.core.base.commands import BaseCommand


class ListClustersCommand(BaseCommand):
    def __init__(self, request: ClustersListRequestDTO):
        self.request: ClustersListRequestDTO = request

    def execute(self) -> ClustersListResponse:
        return self.request.api.list_clusters(self.request.status)


class GetClusterCommand(BaseCommand):
    def __init__(self, request: ClustersGetRequestDTO):
        self.request: ClustersGetRequestDTO = request

    def execute(self) -> ClusterResponse:
        return self.request.api.describe_cluster(self.request.cluster_id)


class DeleteClusterCommand(BaseCommand):
    def __init__(self, request: ClustersDeleteRequestDTO):
        self.request: ClustersDeleteRequestDTO = request

    def execute(self) -> ClusterDeleteResponse:
        return self.request.api.delete_cluster(self.request.cluster_id)


class CreateClusterCommand(BaseCommand):
    def __init__(
        self,
        request: ClustersCreateRequestDTO,
    ):
        self.request: ClustersCreateRequestDTO = request

    def execute(self) -> ClusterCreateResponse:
        return self.request.api.create_cluster(self.request.to_api_model())


class DeployClusterCommand(BaseCommand):
    def __init__(self, request: ClustersDeployRequestDTO):
        self.request: ClustersDeployRequestDTO = request

    def execute(self) -> ClusterDeployResponse:
        return self.request.api.deploy_cluster(self.request.cluster_id)


class GetClusterNodesCommand(BaseCommand):
    def __init__(self, request: ClustersNodesRequestDTO):
        self.request: ClustersNodesRequestDTO = request

    def execute(self) -> ClusterNodesResponse:
        return self.request.api.get_nodes(self.request.cluster_id)


class AddClusterNodeCommand(BaseCommand):
    def __init__(
        self,
        request: ClustersAddNodeRequestDTO,
    ):
        self.request: ClustersAddNodeRequestDTO = request

    def execute(self) -> ClusterNodesResponse:
        return self.request.api.add_nodes(
            self.request.cluster_id, self.request.to_api_model()
        )


class DeleteClusterNodeCommand(BaseCommand):
    def __init__(self, request: ClustersDeleteNodeRequestDTO):
        self.request: ClustersDeleteNodeRequestDTO = request

    def execute(self) -> ClusterNodeRemoveResponse:
        return self.request.api.delete_node_from_cluster(
            self.request.cluster_id, self.request.node_id
        )


class GetClusterResourcesCommand(BaseCommand):
    def __init__(self, request: ClustersResourcesRequestDTO):
        self.request: ClustersResourcesRequestDTO = request

    def execute(self) -> ClusterResourcesListResponse:
        return self.request.api.get_cluster_resources(self.request.cluster_id)


class ListCloudCredentialsCommand(BaseCommand):
    def __init__(self, request: ListCloudCredentialsRequestDTO):
        self.request: ListCloudCredentialsRequestDTO = request

    def execute(self) -> CredentialsListResponse:
        return self.request.api.list_credentials()


class DownloadKubeConfigCommand(BaseCommand):
    def __init__(self, request: ClustersDownloadKubeConfigRequestDTO):
        self.request: ClustersDownloadKubeConfigRequestDTO = request

    def execute(self) -> ClusterKubeconfigResponse:
        return self.request.api.get_cluster_kubeconfig(self.request.cluster_id)
