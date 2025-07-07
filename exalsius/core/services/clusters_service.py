from typing import List, Optional, Tuple

from exalsius_api_client.models.cluster_create_response import ClusterCreateResponse
from exalsius_api_client.models.cluster_nodes_response import ClusterNodesResponse
from exalsius_api_client.models.cluster_resources_list_response import (
    ClusterResourcesListResponse,
)
from exalsius_api_client.models.cluster_response import ClusterResponse
from exalsius_api_client.models.cluster_services_response import ClusterServicesResponse
from exalsius_api_client.models.clusters_list_response import ClustersListResponse

from exalsius.core.operations.clusters_operations import (
    AddClusterNodeOperation,
    CreateClusterOperation,
    DeleteClusterOperation,
    DeployClusterOperation,
    GetClusterNodesOperation,
    GetClusterOperation,
    GetClusterResourcesOperation,
    GetClusterServicesOperation,
    ListClustersOperation,
)
from exalsius.core.services.base import BaseService


class ClustersService(BaseService):
    def list_clusters(
        self, status: Optional[str]
    ) -> Tuple[List[ClustersListResponse], Optional[str]]:
        return self.execute_operation(
            ListClustersOperation(
                self.api_client,
                status,
            )
        )

    def get_cluster(self, cluster_id: str) -> Tuple[ClusterResponse, Optional[str]]:
        return self.execute_operation(
            GetClusterOperation(
                self.api_client,
                cluster_id,
            )
        )

    def delete_cluster(self, cluster_id: str) -> Tuple[ClusterResponse, Optional[str]]:
        return self.execute_operation(
            DeleteClusterOperation(
                self.api_client,
                cluster_id,
            )
        )

    def create_cluster(
        self, name: str, k8s_version: str
    ) -> Tuple[ClusterCreateResponse, Optional[str]]:
        return self.execute_operation(
            CreateClusterOperation(
                self.api_client,
                name,
                k8s_version,
            )
        )

    def deploy_cluster(self, cluster_id: str) -> Tuple[ClusterResponse, Optional[str]]:
        return self.execute_operation(
            DeployClusterOperation(
                self.api_client,
                cluster_id,
            )
        )

    def get_cluster_services(
        self, cluster_id: str
    ) -> Tuple[ClusterServicesResponse, Optional[str]]:
        return self.execute_operation(
            GetClusterServicesOperation(
                self.api_client,
                cluster_id,
            )
        )

    def get_cluster_nodes(
        self, cluster_id: str
    ) -> Tuple[ClusterNodesResponse, Optional[str]]:
        return self.execute_operation(
            GetClusterNodesOperation(
                self.api_client,
                cluster_id,
            )
        )

    def add_cluster_node(
        self, cluster_id: str, node_ids: List[str], node_role: str
    ) -> Tuple[ClusterNodesResponse, Optional[str]]:
        return self.execute_operation(
            AddClusterNodeOperation(
                self.api_client,
                cluster_id,
                node_ids,
                node_role,
            )
        )

    def get_cluster_resources(
        self, cluster_id: str
    ) -> Tuple[Optional[ClusterResourcesListResponse], Optional[str]]:
        return self.execute_operation(
            GetClusterResourcesOperation(self.api_client, cluster_id)
        )
