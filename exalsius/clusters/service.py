import datetime
from typing import List, Optional

from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.cluster_create_response import ClusterCreateResponse
from exalsius_api_client.models.cluster_delete_response import ClusterDeleteResponse
from exalsius_api_client.models.cluster_deploy_response import ClusterDeployResponse
from exalsius_api_client.models.cluster_nodes_response import ClusterNodesResponse
from exalsius_api_client.models.cluster_resources_list_response import (
    ClusterResourcesListResponse,
)
from exalsius_api_client.models.cluster_response import ClusterResponse
from exalsius_api_client.models.cluster_services_response import ClusterServicesResponse
from exalsius_api_client.models.clusters_list_response import ClustersListResponse
from exalsius_api_client.models.credentials import Credentials

from exalsius.clusters.commands import (
    AddClusterNodeCommand,
    CreateClusterCommand,
    DeleteClusterCommand,
    DeployClusterCommand,
    GetClusterCommand,
    GetClusterNodesCommand,
    GetClusterResourcesCommand,
    GetClusterServicesCommand,
    ListCloudCredentialsCommand,
    ListClustersCommand,
)
from exalsius.clusters.models import (
    ClustersAddNodeRequestDTO,
    ClustersCreateRequestDTO,
    ClustersDeleteRequestDTO,
    ClustersDeployRequestDTO,
    ClustersGetRequestDTO,
    ClustersListRequestDTO,
    ClustersNodesRequestDTO,
    ClustersResourcesRequestDTO,
    ClustersServicesRequestDTO,
    ClusterType,
    ListCloudCredentialsRequestDTO,
    NodesToAddDTO,
    ServiceDeploymentDTO,
)
from exalsius.config import AppConfig
from exalsius.core.base.commands import BaseCommand
from exalsius.core.base.service import BaseServiceWithAuth, T
from exalsius.core.commons.models import ServiceError


class ClustersService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.clusters_api: ClustersApi = ClustersApi(self.api_client)
        self.management_api: ManagementApi = ManagementApi(self.api_client)

    def _execute_command(self, command: BaseCommand[T]) -> T:
        try:
            return command.execute()
        except ApiException as e:
            raise ServiceError(
                f"api error while executing command {command.__class__.__name__}. "
                f"Error code: {e.status}, error body: {e.body}"
            )
        except Exception as e:
            raise ServiceError(
                f"unexpected error while executing command {command.__class__.__name__}: {e}"
            )

    def list_clusters(self, status: Optional[str]) -> ClustersListResponse:
        return self.execute_command(
            ListClustersCommand(
                ClustersListRequestDTO(
                    api=self.clusters_api,
                    status=status,
                )
            )
        )

    def get_cluster(self, cluster_id: str) -> ClusterResponse:
        return self.execute_command(
            GetClusterCommand(
                ClustersGetRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                )
            )
        )

    def delete_cluster(self, cluster_id: str) -> ClusterDeleteResponse:
        return self.execute_command(
            DeleteClusterCommand(
                ClustersDeleteRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                )
            )
        )

    # TODO: Revisit this to improve the interface to the CLI
    def create_cluster(
        self,
        name: str,
        cluster_type: ClusterType,
        colony_id: Optional[str] = None,
        k8s_version: Optional[str] = None,
        to_be_deleted_at: Optional[datetime.datetime] = None,
        control_plane_node_ids: Optional[List[str]] = None,
        worker_node_ids: Optional[List[str]] = None,
        service_deployments: Optional[List[ServiceDeploymentDTO]] = None,
    ) -> ClusterCreateResponse:
        return self.execute_command(
            CreateClusterCommand(
                ClustersCreateRequestDTO(
                    api=self.clusters_api,
                    name=name,
                    cluster_type=cluster_type,
                    colony_id=colony_id,
                    k8s_version=k8s_version,
                    to_be_deleted_at=to_be_deleted_at,
                    control_plane_node_ids=control_plane_node_ids,
                    worker_node_ids=worker_node_ids,
                    service_deployments=service_deployments,
                )
            )
        )

    def deploy_cluster(self, cluster_id: str) -> ClusterDeployResponse:
        return self.execute_command(
            DeployClusterCommand(
                ClustersDeployRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                )
            )
        )

    def get_cluster_services(self, cluster_id: str) -> ClusterServicesResponse:
        return self.execute_command(
            GetClusterServicesCommand(
                ClustersServicesRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                )
            )
        )

    def get_cluster_nodes(self, cluster_id: str) -> ClusterNodesResponse:
        return self.execute_command(
            GetClusterNodesCommand(
                ClustersNodesRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                )
            )
        )

    def add_cluster_node(
        self, cluster_id: str, nodes_to_add: List[NodesToAddDTO]
    ) -> ClusterNodesResponse:
        return self.execute_command(
            AddClusterNodeCommand(
                ClustersAddNodeRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                    nodes_to_add=nodes_to_add,
                )
            )
        )

    def get_cluster_resources(self, cluster_id: str) -> ClusterResourcesListResponse:
        return self.execute_command(
            GetClusterResourcesCommand(
                ClustersResourcesRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                )
            )
        )

    def list_cloud_credentials(self) -> List[Credentials]:
        return self.execute_command(
            ListCloudCredentialsCommand(
                ListCloudCredentialsRequestDTO(
                    api=self.management_api,
                )
            )
        )
